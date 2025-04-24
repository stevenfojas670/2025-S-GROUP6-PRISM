"""
This module analyzes similarity scores between student submissions
and clusters both students and submission pairs to detect anomalies.
"""

import os
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from statistics import mean, pvariance

import numpy as np
from scipy.stats import kurtosis, skew
from sklearn.cluster import KMeans
from sklearn.discriminant_analysis import StandardScaler

from django.db import transaction
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
    """
    Delete StudentReport rows for an assignment except the one we just created.

    We first collect all AssignmentReport IDs for this assignment except the
    one we want to keep, then remove every StudentReport tied to those older
    reports. This keeps our reporting table lean and avoids stale data.
    """
    # Gather obsolete report IDs in one query
    old_ids = (
        AssignmentReport.objects
        .filter(assignment=assignment)
        .exclude(id=keep_report_id)
        .values_list('id', flat=True)
    )

    # Delete all StudentReport rows for those old reports
    StudentReport.objects.filter(report_id__in=old_ids).delete()


def flag_student_pairs(report, professor, cutoff=2.0):
    """
    Flag all similarity pairs for students with z_score > cutoff.

    We:
    1. Identify suspect submissions in one query.
    2. Clear old flags for this professor and assignment.
    3. Bulk-fetch all similarity pairs involving any suspect.
    4. Build FlaggedStudents objects in memory.
    5. Insert them in one bulk_create to minimize DB hits.
    Returns the number of new flags created.
    """
    # 1) Find suspect submission IDs
    suspects = report.student_reports.filter(z_score__gt=cutoff)
    sub_ids = list(suspects.values_list('submission_id', flat=True))
    if not sub_ids:
        return 0

    # 2) Clear previous flags in one go
    FlaggedStudents.objects.filter(
        professor=professor,
        similarity__assignment=report.assignment
    ).delete()

    # 3) Fetch all relevant similarity pairs in one query
    pairs = (
        SubmissionSimilarityPairs.objects
        .filter(assignment=report.assignment)
        .filter(
            Q(submission_id_1__in=sub_ids) |
            Q(submission_id_2__in=sub_ids)
        )
        .select_related('submission_id_1__student',
                        'submission_id_2__student')
    )

    # 4) Group pairs by submission for quick lookups
    by_sub = defaultdict(list)
    for p in pairs:
        by_sub[p.submission_id_1_id].append(p)
        by_sub[p.submission_id_2_id].append(p)

    # 5) Build FlaggedStudents objects in memory
    flags = []
    for sr in suspects:
        student = sr.submission.student
        for pair in by_sub.get(sr.submission_id, []):
            flags.append(
                FlaggedStudents(
                    professor=professor,
                    student=student,
                    similarity=pair,
                    generative_ai=False
                )
            )

    # 6) Bulk insert to minimize DB round-trips
    with transaction.atomic():
        created = FlaggedStudents.objects.bulk_create(
            flags, ignore_conflicts=True
        )
    return len(created)


def generate_reports_for_course_semester(
    course_id,
    semester_id,
    max_workers=min(32, os.cpu_count() * 5)
):
    """
    Run generate_report in parallel for all assignments of a course+semester.

    We:
    1. Fetch all assignment IDs in one query.
    2. Schedule generate_report for each in a ThreadPoolExecutor.
    This speeds up processing by leveraging multiple threads.
    """
    # 1) Collect assignment IDs
    assignment_ids = list(
        Assignments.objects
        .filter(
            course_catalog_id=course_id,
            semester_id=semester_id
        )
        .values_list('id', flat=True)
    )
    print(f'\n📦 Found {len(assignment_ids)} assignments '
          f'for course={course_id}, semester={semester_id}')
    if not assignment_ids:
        print('⚠️ No assignments to process.')
        return

    # 2) Parallel execution
    print(f'🚀 Parallel report generation with '
          f'max_workers={max_workers}')
    start = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for aid in assignment_ids:
            print(f'  🔄 Scheduling generate_report({aid})')
        # map returns as they complete; any exception bubbles out
        executor.map(generate_report, assignment_ids)

    elapsed = time.time() - start
    print(f'\n✅ Finished in {elapsed:.2f}s')


def bulk_recompute_semester_profiles(
    course_id,
    semester_id,
    z_threshold: float = 2.0,
    sim_threshold: float = 45.0
):
    """
    Recompute StudentSemesterProfile for every student in a course+semester.

    We:
    1. Fetch raw z_score and mean_similarity for all submissions.
    2. Group them by student in memory.
    3. Compute 7 features per student.
    4. Bulk-create all profiles in one transaction.
    """
    print(f'[START] bulk_recompute_semester_profiles '
          f'for {course_id}/{semester_id}')
    t0 = time.time()

    # 1) Fetch data in one go
    rows = StudentReport.objects.filter(
        submission__assignment__course_catalog_id=course_id,
        submission__assignment__semester_id=semester_id
    ).values(
        'submission__student_id', 'z_score', 'mean_similarity'
    )

    # 2) Group by student
    buckets = defaultdict(lambda: {'zs': [], 'sims': []})
    for r in rows:
        sid = r['submission__student_id']
        buckets[sid]['zs'].append(r['z_score'])
        buckets[sid]['sims'].append(r['mean_similarity'])

    profiles = []
    # 3) Compute metrics and build model instances
    for sid, data in buckets.items():
        zs = data['zs']
        sims = data['sims']
        count = len(zs)

        if count == 0:
            avg_z = max_z = num_flag = sim_var = sim_sk = sim_kt = high_frac = 0.0
        else:
            avg_z = mean(zs)
            max_z = max(zs)
            num_flag = sum(1 for z in zs if z > z_threshold)
            sim_var = pvariance(sims)
            sim_sk = skew(sims) if len(sims) >= 3 and sim_var else 0.0
            sim_kt = kurtosis(sims) if len(sims) >= 3 and sim_var else 0.0
            # new definition: fraction of flagged submissions
            high_frac = num_flag / count

        vec = [
            avg_z, max_z, num_flag,
            sim_var, sim_sk, sim_kt, high_frac
        ]

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
                feature_vector=vec
            )
        )

    # 4) Bulk insert to minimize DB hits
    with transaction.atomic():
        StudentSemesterProfile.objects.bulk_create(profiles)

    print(f'[DONE] in {time.time() - t0:.1f}s')


def run_kmeans_for_course_semester(
    course_id,
    semester_id,
    n_clusters=6,
    random_state=0,
    b_refs=10,
    sim_threshold=45.0
):
    """
    Cluster students based on their semester profiles:

    1. Load all StudentSemesterProfile entries.
    2. Stack their 7-dim vectors → X_raw.
    3. Apply feature weights and standardize → X_scaled.
    4. Use gap statistic to pick optimal k in [2..n_clusters].
    5. Fit KMeans(best_k) and remap labels so 0 is lowest-risk cluster.
    6. Bulk-update cluster_label on StudentSemesterProfile.
    """
    # 1) Fetch profiles in one query
    profiles = list(
        StudentSemesterProfile.objects.filter(
            course_catalog_id=course_id,
            semester_id=semester_id
        )
    )
    if not profiles:
        return None

    # Preserve student ordering for downstream use
    ids = [p.student_id for p in profiles]

    # 2) Stack into a matrix
    X_raw = np.vstack([p.feature_vector for p in profiles])

    # 3) Apply weights and standardize
    weights = np.array([
        1.0, 1.5, 1.2, 0.5, 0.5, 0.5, 1.5
    ], dtype=float)
    X_weighted = X_raw * weights
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_weighted)

    # Gap statistic to find best_k
    def dispersion(data, labels, centers):
        return sum(
            np.sum((data[labels == i] - c) ** 2)
            for i, c in enumerate(centers)
        )

    mins, maxs = X_scaled.min(axis=0), X_scaled.max(axis=0)
    best_k, best_gap = None, -np.inf

    for k in range(2, n_clusters + 1):
        km_ref = KMeans(n_clusters=k, random_state=random_state)
        km_ref.fit(X_scaled)
        Wk = dispersion(X_scaled, km_ref.labels_, km_ref.cluster_centers_)
        logWk = np.log(Wk)

        ref_logs = []
        for _ in range(b_refs):
            Xb = np.random.uniform(mins, maxs, X_scaled.shape)
            kmb = KMeans(n_clusters=k, random_state=random_state)
            kmb.fit(Xb)
            Wkb = dispersion(Xb, kmb.labels_, kmb.cluster_centers_)
            ref_logs.append(np.log(Wkb))

        gap_k = np.mean(ref_logs) - logWk
        if gap_k > best_gap:
            best_gap, best_k = gap_k, k

    # 5) Fit final KMeans with best_k
    final_km = KMeans(n_clusters=best_k, random_state=random_state)
    labels = final_km.fit_predict(X_scaled)
    final_km._fit_student_ids_ = ids

    # 6) Remap clusters by a composite risk score
    centers = final_km.cluster_centers_
    raw_centers = scaler.inverse_transform(centers) / weights
    # Composite: 2×avg_z + 1.5×max_z + 1.5×high_frac
    composite = (
        2.0 * raw_centers[:, 0] +
        1.5 * raw_centers[:, 1] +
        1.5 * raw_centers[:, 6]
    )
    order = np.argsort(composite)
    remap = {old: new for new, old in enumerate(order)}

    # 7) Apply remapped labels in memory
    for profile, lbl in zip(profiles, labels):
        profile.cluster_label = remap[int(lbl)]

    # 8) Bulk-update all profiles in one transaction
    with transaction.atomic():
        StudentSemesterProfile.objects.bulk_update(
            profiles, ['cluster_label']
        )

    return final_km
