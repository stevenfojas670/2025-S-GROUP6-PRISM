"""
This module contains functions to analyze similarity scores between student submissions.

It provides:
- get_all_scores_by_student: fetches and deduplicates similarity pairs per assignment
- compute_population_stats: computes overall mean and population std. dev.
- compute_student_z_score: student-level z-score with optional finite-pop correction
- compute_student_confidence_interval: normal-based CI for each student’s mean
- update_all_pair_stats: builds PairFlagStat table in one bulk operation
- generate_report: orchestrates report creation and student flagging in bulk
"""

import math
import time
from collections import defaultdict
from typing import Dict, List, Tuple

from django.db import models, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from scipy.stats import norm
from assignments.models import Assignments, Submissions
from cheating.models import (
    AssignmentReport,
    FlaggedStudents,
    PairFlagStat,
    StudentReport,
    SubmissionSimilarityPairs,
)


def get_all_scores_by_student(assignment: Assignments) -> Dict[int, List[float]]:
    """
    Fetch and deduplicate all similarity scores for an assignment.

    We only keep each unordered pair once by enforcing submission_id_1 < submission_id_2.
    Returns a map: submission_id -> list of similarity percentages.
    """
    # 1) Get all similarity records for this assignment
    pairs = SubmissionSimilarityPairs.objects.filter(assignment=assignment)

    # 2) Filter out reverse duplicates (keep only id1 < id2)
    pairs = pairs.filter(
        submission_id_1_id__lt=models.F("submission_id_2_id")
    )

    # 3) Accumulate scores per submission into a dict of lists
    scores = defaultdict(list)
    for p in pairs:
        s1 = p.submission_id_1_id
        s2 = p.submission_id_2_id
        pct = p.percentage
        scores[s1].append(pct)
        scores[s2].append(pct)

    return scores


def compute_population_stats(
    scores_by_student: Dict[int, List[float]]
) -> Tuple[float, float]:
    """
    Compute population mean (mu) and std deviation (sigma) of all scores.

    Treats the flattened list of all student scores as the full population
    (divides variance by N, no Bessel correction).
    """
    # 1) Flatten the lists
    all_scores: List[float] = []
    for lst in scores_by_student.values():
        all_scores.extend(lst)

    N = len(all_scores)
    if N == 0:
        raise ValueError("No scores available to compute statistics.")

    # 2) Compute mean
    total = sum(all_scores)
    mu = total / N

    # 3) Compute population variance
    sum_sq = sum((x - mu) ** 2 for x in all_scores)
    variance = sum_sq / N

    # 4) Return mean and std dev
    sigma = math.sqrt(variance)
    return mu, sigma


def compute_student_z_score(
    scores: List[float],
    mu: float,
    sigma: float,
    use_fpc: bool = True,
    population_size: int = None,
) -> Tuple[float, float]:
    """
    Compute a student’s mean and z-score.

    SE = sigma / sqrt(n), optionally multiplied by finite-population correction:
      FPC = sqrt((N - n) / (N - 1))
    Returns: (mean_i, z_i).
    """
    n = len(scores)
    if n == 0:
        raise ValueError("Cannot compute z-score on empty list.")

    # 1) Sample mean
    mean_i = sum(scores) / n

    # 2) Standard error
    se = sigma / math.sqrt(n)

    # 3) Finite-population correction
    if use_fpc:
        if population_size is None:
            raise ValueError("population_size required when use_fpc=True")
        N = population_size
        if N <= n:
            raise ValueError("population_size must exceed sample size")
        fpc = math.sqrt((N - n) / (N - 1))
        se *= fpc

    # 4) Z-score
    z_i = (mean_i - mu) / se
    return mean_i, z_i


def compute_student_confidence_interval(
    scores: List[float],
    sigma: float,
    conf_level: float = 0.95,
    use_fpc: bool = True,
    population_size: int = None,
) -> Tuple[float, float]:
    """
    Compute a two-sided confidence interval for a student’s mean.

    Uses known-population sigma and normal approximation:
      CI = mean ± z_crit * SE
    """
    n = len(scores)
    if n == 0:
        raise ValueError("Cannot compute CI on empty list.")

    mean_i = sum(scores) / n
    se = sigma / math.sqrt(n)

    if use_fpc:
        if population_size is None:
            raise ValueError("population_size required when use_fpc=True")
        N = population_size
        if N <= n:
            raise ValueError("population_size must exceed sample size")
        se *= math.sqrt((N - n) / (N - 1))

    alpha = 1.0 - conf_level
    z_crit = norm.ppf(1.0 - alpha / 2.0)
    lower = mean_i - z_crit * se
    upper = mean_i + z_crit * se
    return lower, upper


def update_all_pair_stats(
    course_id: int,
    semester_id: int,
    flagged_data: List[Dict[str, float]],
) -> int:
    """
    Rebuild PairFlagStat for a course+semester in one bulk operation.

    flagged_data: list of dicts with keys "student_a", "student_b", "sim", "z".
    """
    # 1) Remove old stats in one query
    PairFlagStat.objects.filter(
        course_catalog_id=course_id,
        semester_id=semester_id,
    ).delete()

    # 2) Single scan of all raw similarity pairs
    qs = SubmissionSimilarityPairs.objects.filter(
        assignment__course_catalog_id=course_id,
        assignment__semester_id=semester_id,
    ).values(
        "submission_id_1__student_id",
        "submission_id_2__student_id",
        "percentage",
    )

    stats = defaultdict(lambda: {
        "assignments_shared": 0,
        "total_similarity": 0.0,
        "flagged_count": 0,
        "total_z_score": 0.0,
        "max_z_score": 0.0,
    })

    # 2a) Accumulate assignment counts and similarity sums
    for row in qs:
        a = row["submission_id_1__student_id"]
        b = row["submission_id_2__student_id"]
        if a > b:
            a, b = b, a
        rec = stats[(a, b)]
        rec["assignments_shared"] += 1
        rec["total_similarity"] += row["percentage"]

    # 2b) Layer on flagged info
    for d in flagged_data:
        a, b = d["student_a"], d["student_b"]
        rec = stats[(a, b)]
        rec["flagged_count"] += 1
        rec["total_z_score"] += d["z"]
        rec["max_z_score"] = max(rec["max_z_score"], d["z"])

    # 3) Build model instances
    to_create = []
    for (a, b), rec in stats.items():
        to_create.append(PairFlagStat(
            course_catalog_id=course_id,
            semester_id=semester_id,
            student_a_id=a,
            student_b_id=b,
            assignments_shared=rec["assignments_shared"],
            total_similarity=rec["total_similarity"],
            flagged_count=rec["flagged_count"],
            total_z_score=rec["total_z_score"],
            max_z_score=rec["max_z_score"],
        ))

    # 4) Bulk-create in one transaction
    with transaction.atomic():
        PairFlagStat.objects.bulk_create(to_create)

    return len(to_create)


def generate_report(assignment_id: int) -> Tuple[AssignmentReport, List[dict]]:
    """
    Create AssignmentReport + StudentReport in bulk, then flag students in one pass.

    Returns:
      - report: the created AssignmentReport
      - flagged_data: list of dicts suitable for update_all_pair_stats
    """
    print(f"\n⏳ [START] generate_report({assignment_id})")
    t0 = time.time()

    # 1) Load assignment and get all similarity scores
    assignment = get_object_or_404(Assignments, pk=assignment_id)
    scores_map = get_all_scores_by_student(assignment)

    # 2) Compute global stats
    mu, sigma = compute_population_stats(scores_map)
    variance = sigma * sigma
    total_pairs = sum(len(v) for v in scores_map.values()) // 2
    print(f"  • Stats: μ={mu:.2f}, σ={sigma:.2f}, pairs={total_pairs}")

    flagged_data: List[dict] = []

    with transaction.atomic():
        # 3) Create the AssignmentReport
        report = AssignmentReport.objects.create(
            assignment=assignment,
            mu=mu,
            sigma=sigma,
            variance=variance,
        )

        # 4) Bulk-create StudentReport rows
        sr_objs = []
        for sub_id, sims in scores_map.items():
            mean_sim = sum(sims) / len(sims)
            _, z_val = compute_student_z_score(
                scores=sims,
                mu=mu,
                sigma=sigma,
                use_fpc=True,
                population_size=total_pairs,
            )
            lo, hi = compute_student_confidence_interval(
                scores=sims,
                sigma=sigma,
                conf_level=0.95,
                use_fpc=True,
                population_size=total_pairs,
            )
            sr_objs.append(StudentReport(
                report=report,
                submission_id=sub_id,
                mean_similarity=mean_sim,
                z_score=z_val,
                ci_lower=lo,
                ci_upper=hi,
            ))
        StudentReport.objects.bulk_create(sr_objs)
        print(f"    ✔️ Bulk-created {len(sr_objs)} StudentReport rows")

        # 5) Flag high-z students in one bulk pass
        cutoff = 2.0
        suspects = report.student_reports.filter(z_score__gt=cutoff)
        sub_ids = list(suspects.values_list("submission_id", flat=True))

        if sub_ids:
            # Fetch all pairs involving any suspect in one query
            all_pairs = SubmissionSimilarityPairs.objects.filter(
                assignment=assignment
            ).filter(
                Q(submission_id_1__in=sub_ids) |
                Q(submission_id_2__in=sub_ids)
            ).select_related(
                "submission_id_1__student",
                "submission_id_2__student"
            )

            # Group and flag in memory
            by_sub = defaultdict(list)
            for p in all_pairs:
                by_sub[p.submission_id_1_id].append(p)
                by_sub[p.submission_id_2_id].append(p)

            # Determine professor to assign flags
            first_sub = Submissions.objects.filter(
                assignment=assignment
            ).select_related("course_instance__professor"
            ).first()
            prof = (
                first_sub.course_instance.professor
                if first_sub else None
            )

            flags = []
            for sr in suspects:
                student = sr.submission.student
                for pair in by_sub.get(sr.submission_id, []):
                    sim = pair.percentage
                    z_val = (sim - mu) / sigma if sigma else 0.0

                    if prof:
                        flags.append(FlaggedStudents(
                            professor=prof,
                            student=student,
                            similarity=pair,
                            generative_ai=False,
                        ))

                    a_id = pair.submission_id_1.student_id
                    b_id = pair.submission_id_2.student_id
                    if a_id > b_id:
                        a_id, b_id = b_id, a_id
                    flagged_data.append({
                        "student_a": a_id,
                        "student_b": b_id,
                        "sim": sim,
                        "z": z_val,
                    })

            if flags:
                FlaggedStudents.objects.bulk_create(
                    flags, ignore_conflicts=True
                )
                print(f"    🚩 Inserted {len(flags)} FlaggedStudents")
        else:
            print("    ⚠️ No students above cutoff; skipping flagging")

    duration = time.time() - t0
    print(f"✅ [DONE] generate_report({assignment_id}) in {duration:.2f}s")
    return report, flagged_data