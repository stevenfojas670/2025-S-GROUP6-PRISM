"""
This module contains functions to analyze similarity scores between student submissions.
It computes a feature vector for each student based on their submission reports,
and clusters students into groups based on these features.
"""

import os
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from statistics import mean, pvariance
from scipy.stats import skew, kurtosis
from django.db import transaction
from sklearn.cluster import KMeans
import time
from sklearn.discriminant_analysis import StandardScaler
from django.db.models import Q
from assignments.models import Assignments
from .models import (
    AssignmentReport,
    FlaggedStudents,
    StudentReport,
    StudentSemesterProfile,
    SubmissionSimilarityPairs,
)
from cheating.utils.similarity_analysis import generate_report


def cleanup_old_student_reports(assignment, keep_report_id):
    """Delete all StudentReports (old) for the given assignment.

    That are tied to older AssignmentReports (i.e., not the newly created one).
    Args:
        assignment (Assignments): Assignment instance.
        keep_report_id (int): The ID of the AssignmentReport to retain.
    """
    # Here I’m fetching all previous reports for this assignment,
    # except for the one we just created (the new one).
    # I only want to remove reports that are now obsolete.
    old_report_ids = (
        AssignmentReport.objects.filter(assignment=assignment)
        .exclude(id=keep_report_id)
        .values_list("id", flat=True)
    )

    # Then I delete every StudentReport that was tied to those older reports.
    # This ensures we don't keep outdated analysis in the database.
    StudentReport.objects.filter(report_id__in=old_report_ids).delete()


def flag_student_pairs(report, professor, cutoff=2.0):
    """
    Flag all similarity pairs involving students with z > cutoff.

    Before inserting, deletes any existing FlaggedStudents for this
    assignment/professor to avoid duplicates from older reports.

    Args:
        report (AssignmentReport): the current report instance.
        professor (Professors): professor doing the flagging.
        cutoff (float): z-score cutoff (default = 1.282 for 90%).
        cutoff (float): z-score cutoff (default = 2 for 95%).
    Returns:
        int: number of new FlaggedStudents created.
    """
    created_rows = []

    # First, I collect all students from this report who have a z-score
    # greater than our suspicious threshold (by default, z > 1.282).
    # These are the students we’re going to investigate further.
    suspects = report.student_reports.filter(z_score__gt=cutoff)

    if not suspects.exists():
        return 0

    # Before flagging anything new, I clear out any previous flags
    # this professor made for this assignment. This prevents duplication
    # from multiple runs of this analysis.
    FlaggedStudents.objects.filter(
        professor=professor,
        similarity__assignment=report.assignment,
    ).delete()

    # Now I go through each suspicious student to identify their submission.
    # Then I look up all similarity pairs where their submission was involved.
    for sr in suspects:
        submission = sr.submission
        student = submission.student

        pairs = SubmissionSimilarityPairs.objects.filter(
            assignment=report.assignment,
        ).filter(Q(submission_id_1=submission) | Q(submission_id_2=submission))

        # For every similarity pair involving the student, I prepare a row
        # that will go into the FlaggedStudents table.
        # This helps us trace back who was flagged and why.
        for pair in pairs:
            created_rows.append(
                FlaggedStudents(
                    professor=professor,
                    student=student,
                    similarity=pair,
                    generative_ai=False,
                )
            )

    # I bulk insert all the flagged pairs into the database at once.
    # I also make sure that if some are duplicates, we ignore them.
    inserted = FlaggedStudents.objects.bulk_create(
        created_rows,
        ignore_conflicts=True,
    )

    return len(inserted)


def generate_reports_for_course_semester(
    course_id,
    semester_id,
    max_workers=min(32, os.cpu_count() * 5),
):
    """
    Parallelize report generation across assignments using threads,
    with detailed printouts for manual debugging.
    """
    # here I’m querying the Assignments table to get all assignment IDs
    # that match the given course and semester. I store them as a list
    # so I can later map a report generation function over them in parallel.
    assignment_ids = list(
        Assignments.objects.filter(
            course_catalog_id=course_id, semester_id=semester_id
        ).values_list("id", flat=True)
    )

    print(
        f"\n📦 Found {len(assignment_ids)} assignments for "
        f"course={course_id}, semester={semester_id}"
    )
    if not assignment_ids:
        print(
            "⚠️ No assignments to process—exiting generate_reports_for_course_semester.\n"
        )
        return

    print(
        f"🚀 Starting parallel report generation " f"with max_workers={max_workers}\n"
    )

    t0 = time.time()

    # using ThreadPoolExecutor to parallelize work
    # i map the `generate_report` function to each assignment ID
    # this will speed up report generation by running in multiple threads
    with ThreadPoolExecutor(max_workers=max_workers) as exe:
        for aid in assignment_ids:
            print(f"  🔄 Scheduling generate_report({aid})")
        exe.map(generate_report, assignment_ids)

    t1 = time.time()
    total = t1 - t0

    print(f"\n✅ Finished all report generations in {total:.2f}s")
    print("------------------------------------------------------\n")


def bulk_recompute_semester_profiles(
    course_id,
    semester_id,
    z_threshold: float = 2.0,
    sim_threshold: float = 45.0,  # we no longer use this for high_frac, but leave it for backward compatibility
):
    print(f"[START] bulk_recompute_semester_profiles for {course_id}/{semester_id}")
    t0 = time.time()

    # 1) pull student_id, z_score, mean_similarity
    rows = StudentReport.objects.filter(
        submission__assignment__course_catalog_id=course_id,
        submission__assignment__semester_id=semester_id,
    ).values("submission__student_id", "z_score", "mean_similarity")

    # 2) group by student
    buckets: dict[int, dict[str, list[float]]] = defaultdict(
        lambda: {"zs": [], "sims": []}
    )
    for r in rows:
        sid = r["submission__student_id"]
        buckets[sid]["zs"].append(r["z_score"])
        buckets[sid]["sims"].append(r["mean_similarity"])

    profiles = []
    # 3) compute metrics & build profile objects
    for sid, data in buckets.items():
        zs = data["zs"]
        sims = data["sims"]
        total_subs = len(zs)  # number of assignments submitted

        if total_subs == 0:
            # no submissions → everything zero
            avg_z = max_z = num_flag = sim_var = sim_sk = sim_kt = high_frac = 0.0
        else:
            # here I calculate basic z‐score stats
            avg_z = mean(zs)
            max_z = max(zs)
            # here I count how many assignments exceeded the z_threshold
            num_flag = sum(1 for z in zs if z > z_threshold)

            # similarity moments stay the same
            sim_var = pvariance(sims)
            sim_sk = skew(sims) if len(sims) >= 3 and sim_var != 0 else 0.0
            sim_kt = kurtosis(sims) if len(sims) >= 3 and sim_var != 0 else 0.0

            # here I redefine high_frac = flagged_assignments / total_assignments
            high_frac = num_flag / total_subs

        # 4) assemble a 7-dim feature vector in the same order
        vec = [
            avg_z,
            max_z,
            num_flag,
            sim_var,
            sim_sk,
            sim_kt,
            high_frac,
        ]

        # here I prepare the new or updated profile object
        profiles.append(
            StudentSemesterProfile(
                student_id=sid,
                course_catalog_id=course_id,
                semester_id=semester_id,
                avg_z_score=avg_z,
                max_z_score=max_z,
                num_flagged_assignments=num_flag,
                mean_similarity_variance=sim_var,
                mean_similarity_skewness=sim_sk,
                mean_similarity_kurtosis=sim_kt,
                high_similarity_fraction=high_frac,
                feature_vector=vec,
            )
        )

    # 5) bulk-create all profiles in one atomic transaction
    with transaction.atomic():
        StudentSemesterProfile.objects.bulk_create(profiles)

    print(f"[DONE] bulk_recompute_semester_profiles in {time.time() - t0:.1f}s")


def run_kmeans_for_course_semester(
    course_id,
    semester_id,
    n_clusters=6,
    random_state=0,
    b_refs=10,
    sim_threshold=45.0,
):
    """
    1) Load all StudentSemesterProfile rows for this course+semester
    2) Stack their 7-dim feature_vector → X_raw
    3) Weight & standardize → X_scaled
    4) Use gap-statistic to pick best_k in [2..n_clusters]
    5) Fit & predict KMeans(best_k) on X_scaled
    6) Remap cluster IDs so 0 = lowest composite sim-metric
    7) Bulk-update `cluster_label` on StudentSemesterProfile
    8) Record `_fit_student_ids_` on the returned estimator
    """
    # here I fetch all profiles for the given course & semester
    profiles = list(
        StudentSemesterProfile.objects.filter(
            course_catalog_id=course_id,
            semester_id=semester_id,
        )
    )
    if not profiles:
        return None

    # here I preserve the order of student IDs for downstream use
    student_ids = [p.student_id for p in profiles]

    # here I stack each 7-dim feature_vector into a matrix
    X_raw = np.vstack([p.feature_vector for p in profiles])

    # here I apply per-feature weights (tune these as you like)
    weights = np.array(
        [
            1.0,  # avg_z_score
            1.5,  # max_z_score
            1.2,  # num_flagged_assignments
            0.5,  # mean_similarity_variance
            0.5,  # mean_similarity_skewness
            0.5,  # mean_similarity_kurtosis
            1.5,  # high_similarity_fraction
        ],
        dtype=float,
    )
    X_weighted = X_raw * weights

    # here I standardize so each weighted feature has mean=0, std=1
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_weighted)

    # ────────────────────────────────────
    # here I search for the best k via the gap statistic
    # ────────────────────────────────────
    def _within_dispersion(data, labels, centers):
        return sum(np.sum((data[labels == i] - c) ** 2) for i, c in enumerate(centers))

    mins, maxs = X_scaled.min(axis=0), X_scaled.max(axis=0)
    best_k, best_gap = None, -np.inf

    for k in range(2, n_clusters + 1):
        km_ref = KMeans(n_clusters=k, random_state=random_state).fit(X_scaled)
        Wk = _within_dispersion(X_scaled, km_ref.labels_, km_ref.cluster_centers_)
        logWk = np.log(Wk)

        ref_logs = []
        for _ in range(b_refs):
            Xb = np.random.uniform(mins, maxs, size=X_scaled.shape)
            kmb = KMeans(n_clusters=k, random_state=random_state).fit(Xb)
            Wkb = _within_dispersion(Xb, kmb.labels_, kmb.cluster_centers_)
            ref_logs.append(np.log(Wkb))

        gap_k = np.mean(ref_logs) - logWk
        if gap_k > best_gap:
            best_gap, best_k = gap_k, k

    # ────────────────────────────────────
    # here I fit the final KMeans with best_k
    # ────────────────────────────────────
    final_km = KMeans(n_clusters=best_k, random_state=random_state)
    raw_labels = final_km.fit_predict(X_scaled)
    final_km._fit_student_ids_ = student_ids

    # ────────────────────────────────────
    # here I remap clusters by a composite of:
    #   30% avg_z_score, 20% max_z_score, 50% high_similarity_fraction
    # ────────────────────────────────────
    # 1) pull out the scaled+weighted centroids
    centers_scaled = final_km.cluster_centers_  # shape (k, 7)
    # 2) undo the scaler to get back to weighted-feature space
    centers_weighted = scaler.inverse_transform(centers_scaled)
    # 3) undo the feature weights to recover raw feature values
    centers_raw = centers_weighted / weights[None, :]
    #    now columns are:
    #      0 = avg_z_score, 1 = max_z_score, …, 6 = high_similarity_fraction

    avg_z_vals = centers_raw[:, 0]
    max_z_vals = centers_raw[:, 1]
    high_frac_vals = centers_raw[:, 6]

    # 4) form a single composite score for each cluster
    composite = 2.0 * avg_z_vals + 1.5 * max_z_vals + 1.5 * high_frac_vals

    # 5) sort clusters by that score (lowest → highest), build remap
    order = np.argsort(composite)  # e.g. [2, 0, 1, 3, …]
    remap = {old: new for new, old in enumerate(order)}

    # 6) apply the remapping back to each profile
    for profile, lbl in zip(profiles, raw_labels):
        profile.cluster_label = remap[int(lbl)]

    # here I bulk-persist all updated labels in one atomic transaction
    with transaction.atomic():
        StudentSemesterProfile.objects.bulk_update(profiles, ["cluster_label"])

    return final_km
