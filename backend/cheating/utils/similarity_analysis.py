"""
This module contains functions to analyze similarity scores between student submissions.

It provides functionality to compute population statistics such as mean and standard deviation
of similarity scores for a given assignment. It also includes a function to retrieve all
similarity scores for each student in an assignment.

The main functions are:
- get_all_scores_by_student(assignment): Fetches all similarity scores for a given assignment
- compute_population_stats(scores_by_student): Computes the population mean and standard deviation
  of similarity scores.
"""

from cheating.models import PairFlagStat, SubmissionSimilarityPairs
from collections import defaultdict
from django.db import models
import math
from typing import Dict, List, Tuple
from scipy.stats import norm
import time
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q

from assignments.models import Assignments, Submissions
from cheating.models import (
    AssignmentReport,
    StudentReport,
    FlaggedStudents,
    SubmissionSimilarityPairs,
)


def get_all_scores_by_student(assignment):
    """
    Get all similarity scores for a given assignment.

    Return a dict mapping each submission_id (an integer PK)
    to the list of its similarity
    percentages for the given assignment. We only keep one direction per pair—if both
    A→B and B→A exist in the table, we only count A→B once.
    """
    # 1) FETCH: retrieve every SubmissionSimilarityPairs row for this assignment
    #    - .objects.filter(...) returns a QuerySet of model instances
    #    - No database query actually runs until we iterate over 'pairs'
    pairs = SubmissionSimilarityPairs.objects.filter(assignment=assignment)
    # At this point, 'pairs' is a lazy QuerySet containing all matches for 'assignment'

    # 2) DEDUPLICATE: drop reversed duplicates so each unordered pair appears once
    #    - We enforce submission_id_1_id < submission_id_2_id
    #    - models.F('submission_id_2_id') lets us reference the other field in the same row
    pairs = pairs.filter(submission_id_1_id__lt=models.F("submission_id_2_id"))
    # Now 'pairs' contains only rows where id1 < id2, so (A,B) but not (B,A)
    # this avoids double-counting the same pair in both directions it helps with
    # the accuarcy when calculating standard deviation
    # and mean of the scores

    # 3) ACCUMULATE: build a dict of student_id → list of percentages
    #    - defaultdict(list) creates an empty list for any new key automatically
    scores = defaultdict(list)

    for p in pairs:
        # For each pair instance 'p':
        #   p.submission_id_1_id and p.submission_id_2_id are integer PKs of the submissions
        s1 = p.submission_id_1_id
        s2 = p.submission_id_2_id
        # the IntegerField similarity score
        pct = p.percentage

        # Append this score to both students’ lists:
        scores[s1].append(pct)
        scores[s2].append(pct)

    # After the loop, 'scores' is something like:
    #   {
    #     10: [30, 50, 20, ...],   # student submission 10’s list of n scores
    #     20: [30, 20, 45, ...],   # student submission 20’s list of n scores
    #     ...
    #   }

    return scores


def compute_population_stats(
    scores_by_student: Dict[int, List[float]],
) -> Tuple[float, float]:
    """
    Compute the population mean (mu) and population standard deviation (sigma).

    Given a dict mapping each student to their list of scores, we treat the entire
    flattened list as the full population, so we divide by N (not N–1) for the variance
    (no Bessel’s correction).

    Parameters
    ----------
    scores_by_student : Dict[int, List[float]]
        A mapping from each submission_id to the list of its similarity percentages.

    Returns
    -------
    mu : float
        The population mean of all scores.
    sigma : float
        The population standard deviation of all scores.
    """
    # 1) Flatten all the per-student lists into one master list of scores
    #    We'll iterate over each student's list and extend into 'all_scores'.
    all_scores: List[float] = []  # start with an empty list
    for student_id, student_scores in scores_by_student.items():
        # student_id is e.g. 10, 20, 30; student_scores is a List[float] like [30,50,...]
        for pct in student_scores:
            # append each individual percentage to the master list
            all_scores.append(pct)

    # 2) Count the total number of scores in the population
    #    This is our N, the population size
    N = len(all_scores)
    if N == 0:
        # Protect against division by zero
        raise ValueError("No scores available to compute statistics.")

    # 3) Compute the population mean (mu)
    #    Sum of all scores divided by N
    total_sum = sum(all_scores)  # sum up all percentages
    mu = total_sum / N  # population mean

    # 4) Compute the population variance
    #    Sum of squared deviations from mu, divided by N (not N-1)
    #    variance = (1/N) * Σ (x_i - mu)^2
    sum_squared_diff = 0.0
    for x in all_scores:
        deviation = x - mu  # how far is x from the mean?
        sum_squared_diff += deviation * deviation  # accumulate squared deviation

    variance = sum_squared_diff / N  # population variance

    # 5) Population standard deviation is the square root of the variance
    sigma = math.sqrt(variance)

    # 6) Return the two descriptive statistics
    return mu, sigma


def compute_student_z_score(
    scores: List[float],
    mu: float,
    sigma: float,
    use_fpc: bool = True,
    population_size: int = None,
) -> Tuple[float, float]:
    """
    Compute the sample mean and z‑score for a single student’s scores.

    Args:
        scores: List of similarity percentages for one student (length = n).
        mu: Population mean of all scores.
        sigma: Population std. dev. of all scores.
        use_fpc: If True, apply finite‐population correction (FPC).
        population_size: Total number of unique pairwise scores (N).
                         Required if use_fpc=True.

    Returns:
        mean_i: Sample mean of this student’s scores.
        z_i: The z‑score = (mean_i - mu) / SE, where
             SE = sigma / sqrt(n) * FPC (if used).
    """
    n = len(scores)
    if n == 0:
        raise ValueError("Cannot compute z‑score on empty score list")

    # 1) Compute the sample mean
    total = sum(scores)
    mean_i = total / n

    # 2) Base standard error = sigma / sqrt(n)
    se = sigma / math.sqrt(n)

    # 3) Apply finite‐population correction if requested
    #    FPC = sqrt((N - n) / (N - 1))
    if use_fpc:
        if population_size is None:
            raise ValueError("population_size required when use_fpc=True")
        N = population_size
        if N <= n:
            raise ValueError("population_size must exceed sample size")
        fpc = math.sqrt((N - n) / (N - 1))
        se *= fpc

    # 4) Compute the z‑score
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
    Compute a confidence interval for a single student’s mean similarity.

    Assumes known population sigma, uses normal approximation:
      CI = mean ± z_crit * SE
    where SE = sigma / sqrt(n) * FPC (if used).

    Args:
        scores: List of similarity percentages (length = n).
        sigma: Population std. dev. of all scores.
        conf_level: Confidence level, e.g. 0.95 for 95% CI.
        use_fpc: If True, apply finite‐population correction.
        population_size: Total number of unique pairwise scores (N).
                         Required if use_fpc=True.

    Returns:
        (lower, upper): Tuple of floats for the CI endpoints.
    """
    n = len(scores)
    if n == 0:
        raise ValueError("Cannot compute CI on empty score list")

    # 1) Sample mean
    mean_i = sum(scores) / n

    # 2) Base standard error
    se = sigma / math.sqrt(n)

    # 3) Finite‐population correction if requested
    if use_fpc:
        if population_size is None:
            raise ValueError("population_size required when use_fpc=True")
        N = population_size
        if N <= n:
            raise ValueError("population_size must exceed sample size")
        se *= math.sqrt((N - n) / (N - 1))

    # 4) Determine critical z for two‑sided interval
    alpha = 1.0 - conf_level
    z_crit = norm.ppf(1.0 - alpha / 2.0)

    # 5) Compute interval endpoints
    lower = mean_i - z_crit * se
    upper = mean_i + z_crit * se

    return lower, upper


def update_all_pair_stats(course_id, semester_id, flagged_data):
    """
    Build the entire PairFlagStat table for this course+semester in one go.

    flagged_data is a LIST of dicts with keys:
      "student_a", "student_b", "sim", "z"
    """

    # 1) nuke the old rows
    PairFlagStat.objects.filter(
        course_catalog_id=course_id,
        semester_id=semester_id,
    ).delete()

    # 2) do a single scan of EVERY similarity pair for this course+semester
    qs = SubmissionSimilarityPairs.objects.filter(
        assignment__course_catalog_id=course_id, assignment__semester_id=semester_id
    ).values(
        "submission_id_1__student_id",
        "submission_id_2__student_id",
        "percentage",
    )

    from collections import defaultdict

    stats = defaultdict(
        lambda: {
            "assignments_shared": 0,
            "total_similarity": 0.0,
            "flagged_count": 0,
            "total_z_score": 0.0,
            "max_z_score": 0.0,
        }
    )

    # 2a) accumulate counts & sums for every pair
    for row in qs:
        a = row["submission_id_1__student_id"]
        b = row["submission_id_2__student_id"]
        if a > b:
            a, b = b, a
        rec = stats[(a, b)]
        rec["assignments_shared"] += 1
        rec["total_similarity"] += row["percentage"]

    # 2b) now layer on your flagged info
    for d in flagged_data:
        a, b = d["student_a"], d["student_b"]
        rec = stats[(a, b)]
        rec["flagged_count"] += 1
        rec["total_z_score"] += d["z"]
        rec["max_z_score"] = max(rec["max_z_score"], d["z"])

    # 3) materialize them into a bulk_create list
    to_create = []
    for (a, b), rec in stats.items():
        to_create.append(
            PairFlagStat(
                course_catalog_id=course_id,
                semester_id=semester_id,
                student_a_id=a,
                student_b_id=b,
                assignments_shared=rec["assignments_shared"],
                total_similarity=rec["total_similarity"],
                flagged_count=rec["flagged_count"],
                total_z_score=rec["total_z_score"],
                max_z_score=rec["max_z_score"],
            )
        )

    # 4) blow them all in one shot
    with transaction.atomic():
        PairFlagStat.objects.bulk_create(to_create)

    return len(to_create)


def generate_report(assignment_id):
    """
    1) Builds AssignmentReport + StudentReport
    2) Flags high‑z students (z > 2.0)
    3) Returns (report, flagged_data), where flagged_data is a list of dicts:
         {
           "student_a": int,  # smaller student_id
           "student_b": int,  # larger student_id
           "sim": float,      # raw similarity %
           "z": float,        # z‑score
         }
    """
    print(f"\n⏳ [START] generate_report({assignment_id})")
    t0 = time.time()

    # 1) load assignment & gather per‑student similarity lists
    assignment = get_object_or_404(Assignments, pk=assignment_id)
    scores_map = get_all_scores_by_student(assignment)
    print(f"  • Found similarity for {len(scores_map)} submissions")

    # 2) compute population μ, σ, etc.
    mu, sigma = compute_population_stats(scores_map)
    variance = sigma**2
    total_pairs = sum(len(v) for v in scores_map.values()) // 2
    print(f"  • Stats: μ={mu:.2f}, σ={sigma:.2f}, pairs={total_pairs}")

    flagged_data = []

    with transaction.atomic():
        # 3) create AssignmentReport
        report = AssignmentReport.objects.create(
            assignment=assignment,
            mu=mu,
            sigma=sigma,
            variance=variance,
        )
        print(f"    ✔️ Created AssignmentReport id={report.id}")

        # 4) bulk‑create StudentReport rows
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
            sr_objs.append(
                StudentReport(
                    report=report,
                    submission_id=sub_id,
                    mean_similarity=mean_sim,
                    z_score=z_val,
                    ci_lower=lo,
                    ci_upper=hi,
                )
            )
        StudentReport.objects.bulk_create(sr_objs)
        print(f"    ✔️ Bulk‑created {len(sr_objs)} StudentReport rows")

        # 5) flag high‑z students and collect flagged‐pair info
        cutoff = 2.0
        first_sub = (
            Submissions.objects.filter(assignment=assignment)
            .select_related("course_instance__professor")
            .first()
        )

        if first_sub:
            prof = first_sub.course_instance.professor
            print(f"    • Flagging under Professor id={prof.id}")
            flags = []

            # only consider students whose z_score > cutoff
            for sr in report.student_reports.filter(z_score__gt=cutoff):
                sub = sr.submission
                pairs = SubmissionSimilarityPairs.objects.filter(
                    assignment=assignment
                ).filter(Q(submission_id_1=sub) | Q(submission_id_2=sub))

                for pair in pairs:
                    sim = pair.percentage
                    z_val = (sim - mu) / sigma if sigma else 0.0

                    # queue up FlaggedStudents
                    flags.append(
                        FlaggedStudents(
                            professor=prof,
                            student=sub.student,
                            similarity=pair,
                            generative_ai=False,
                        )
                    )

                    # collect for global pair‐stat rebuild
                    a_id = pair.submission_id_1.student_id
                    b_id = pair.submission_id_2.student_id
                    if a_id > b_id:
                        a_id, b_id = b_id, a_id

                    flagged_data.append(
                        {
                            "student_a": a_id,
                            "student_b": b_id,
                            "sim": sim,
                            "z": z_val,
                        }
                    )

            FlaggedStudents.objects.bulk_create(flags, ignore_conflicts=True)
            print(f"    🚩 Inserted {len(flags)} FlaggedStudents")
        else:
            print("    ⚠️ No submissions; skipped flagging")

    duration = time.time() - t0
    print(f"✅ [DONE] generate_report({assignment_id}) in {duration:.2f}s")
    return report, flagged_data
