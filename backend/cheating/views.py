"""Views for the Cheating app with enhanced filtering, ordering, search, and pagination."""

import io
import math

import matplotlib
from matplotlib import pyplot as plt

from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from rest_framework import filters, viewsets
from django_filters.rest_framework import DjangoFilterBackend

from prism_backend.mixins import CachedViewMixin

from assignments.models import Assignments, Submissions

from .models import (
    CheatingGroups,
    CheatingGroupMembers,
    ConfirmedCheaters,
    FlaggedStudents,
    SubmissionSimilarityPairs,
    LongitudinalCheatingGroups,
    LongitudinalCheatingGroupMembers,
    LongitudinalCheatingGroupInstances,
    AssignmentReport,
    StudentReport,
)

from .serializers import (
    CheatingGroupsSerializer,
    CheatingGroupMembersSerializer,
    ConfirmedCheatersSerializer,
    FlaggedStudentsSerializer,
    SubmissionSimilarityPairsSerializer,
    LongitudinalCheatingGroupsSerializer,
    LongitudinalCheatingGroupMembersSerializer,
    LongitudinalCheatingGroupInstancesSerializer,
)

from .pagination import StandardResultsSetPagination

from .utils.similarity_analysis import (
    compute_population_stats,
    compute_student_confidence_interval,
    compute_student_z_score,
    get_all_scores_by_student,
)

# Set up non-interactive backend for matplotlib
matplotlib.use("Agg")


class CheatingGroupsViewSet(viewsets.ModelViewSet, CachedViewMixin):
    """ViewSet for handling CheatingGroups entries."""

    queryset = CheatingGroups.objects.all()
    serializer_class = CheatingGroupsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["assignment", "cohesion_score"]
    ordering_fields = ["cohesion_score"]
    ordering = ["cohesion_score"]
    search_fields = ["analysis_report_path", "assignment__title"]


class CheatingGroupMembersViewSet(viewsets.ModelViewSet, CachedViewMixin):
    """ViewSet for handling CheatingGroupMembers entries."""

    queryset = CheatingGroupMembers.objects.all()
    serializer_class = CheatingGroupMembersSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["cheating_group", "student"]
    ordering_fields = ["cluster_distance"]
    ordering = ["cluster_distance"]
    search_fields = []


class ConfirmedCheatersViewSet(viewsets.ModelViewSet, CachedViewMixin):
    """ViewSet for handling ConfirmedCheaters entries."""

    queryset = ConfirmedCheaters.objects.all()
    serializer_class = ConfirmedCheatersSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["confirmed_date", "assignment", "student"]
    ordering_fields = ["confirmed_date", "threshold_used"]
    ordering = ["confirmed_date"]
    search_fields = ["assignment__title", "student__first_name", "student__last_name"]


class FlaggedStudentsViewSet(viewsets.ModelViewSet, CachedViewMixin):
    """ViewSet for handling FlaggedStudents entries."""

    queryset = FlaggedStudents.objects.all()
    serializer_class = FlaggedStudentsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["professor", "student", "generative_ai"]
    ordering_fields = ["generative_ai"]
    ordering = ["generative_ai"]
    search_fields = [
        "professor__user__username",
        "student__first_name",
        "student__last_name",
    ]


class SubmissionSimilarityPairsViewSet(viewsets.ModelViewSet, CachedViewMixin):
    """ViewSet for handling SubmissionSimilarityPairs entries."""

    queryset = SubmissionSimilarityPairs.objects.all()
    serializer_class = SubmissionSimilarityPairsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["assignment", "file_name", "match_id"]
    ordering_fields = ["percentage"]
    ordering = ["percentage"]
    search_fields = ["file_name", "assignment__title"]


class LongitudinalCheatingGroupsViewSet(viewsets.ModelViewSet, CachedViewMixin):
    """ViewSet for handling LongitudinalCheatingGroups entries."""

    queryset = LongitudinalCheatingGroups.objects.all()
    serializer_class = LongitudinalCheatingGroupsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["score"]
    ordering_fields = ["score"]
    ordering = ["score"]
    search_fields = []


class LongitudinalCheatingGroupMembersViewSet(viewsets.ModelViewSet, CachedViewMixin):
    """ViewSet for handling LongitudinalCheatingGroupMembers entries."""

    queryset = LongitudinalCheatingGroupMembers.objects.all()
    serializer_class = LongitudinalCheatingGroupMembersSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["longitudinal_cheating_group", "student", "is_core_member"]
    ordering_fields = ["appearance_count"]
    ordering = ["appearance_count"]
    search_fields = []


class LongitudinalCheatingGroupInstancesViewSet(viewsets.ModelViewSet, CachedViewMixin):
    """ViewSet for handling LongitudinalCheatingGroupInstances entries."""

    queryset = LongitudinalCheatingGroupInstances.objects.all()
    serializer_class = LongitudinalCheatingGroupInstancesSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["cheating_group", "longitudinal_cheating_group"]
    ordering_fields = ["appearance_count"]
    ordering = ["appearance_count"]
    search_fields = []


def cleanup_old_student_reports(assignment, keep_report_id):
    """Delete all StudentReports (old) for the given assignment.

    That are tied to older AssignmentReports (i.e., not the newly created one).
    Args:
        assignment (Assignments): Assignment instance.
        keep_report_id (int): The ID of the AssignmentReport to retain.
    """
    # Get all older reports tied to this assignment (except the new one)
    old_report_ids = (
        AssignmentReport.objects.filter(assignment=assignment)
        .exclude(id=keep_report_id)
        .values_list("id", flat=True)
    )

    # Delete all StudentReports tied to those old reports
    StudentReport.objects.filter(report_id__in=old_report_ids).delete()


def flag_student_pairs(report, professor, cutoff=1.282):
    """
    Flag all similarity pairs involving students with z > cutoff.

    Before inserting, deletes any existing FlaggedStudents for this
    assignment/professor to avoid duplicates from older reports.

    Args:
        report (AssignmentReport): the current report instance.
        professor (Professors): professor doing the flagging.
        cutoff (float): z-score cutoff (default = 1.282 for 90%).

    Returns:
        int: number of new FlaggedStudents created.
    """
    created_rows = []

    # 1) Get all flagged students with z > cutoff
    suspects = report.student_reports.filter(z_score__gt=cutoff)

    if not suspects.exists():
        return 0

    # 2) Delete previous flags by this professor for this assignment
    FlaggedStudents.objects.filter(
        professor=professor,
        similarity__assignment=report.assignment,
    ).delete()

    # 3) For each flagged student, fetch their submission and similarity pairs
    for sr in suspects:
        submission = sr.submission
        student = submission.student

        pairs = SubmissionSimilarityPairs.objects.filter(
            assignment=report.assignment,
        ).filter(Q(submission_id_1=submission) | Q(submission_id_2=submission))

        # 4) Create one FlaggedStudents row per pair
        for pair in pairs:
            created_rows.append(
                FlaggedStudents(
                    professor=professor,
                    student=student,
                    similarity=pair,
                    generative_ai=False,
                )
            )

    # 5) Insert all, skip duplicates just in case
    inserted = FlaggedStudents.objects.bulk_create(
        created_rows,
        ignore_conflicts=True,
    )

    return len(inserted)


def generate_report(request, assignment_id):
    """
    Compute and persist an AssignmentReport and related StudentReports.

    This function:
      - Computes population stats (μ, σ, variance).
      - Generates one StudentReport per submission.
      - Flags similarity pairs for students above a z-score cutoff.
      - Ensures only the most recent report and its children are kept.

    Args:
        request (HttpRequest): incoming HTTP request (unused here).
        assignment_id (int): ID of the assignment to analyze.

    Returns:
        JsonResponse: report ID, stats, and number of students flagged.
    """
    # 1) Load the Assignment or raise 404 if not found
    assignment = get_object_or_404(Assignments, pk=assignment_id)

    # 2) Collect all pairwise similarity scores per student submission
    scores_map = get_all_scores_by_student(assignment)
    if not scores_map:
        raise Http404("No similarity data found for this assignment.")

    # 3) Compute μ (mean), σ (std), and total pair count N for finite correction
    mu, sigma = compute_population_stats(scores_map)
    variance = sigma**2
    total_pairs = sum(len(v) for v in scores_map.values()) // 2

    # 4) Perform all DB changes in a transaction for atomicity
    with transaction.atomic():
        # 4a) Create the new AssignmentReport
        report = AssignmentReport.objects.create(
            assignment=assignment,
            mu=mu,
            sigma=sigma,
            variance=variance,
        )

        # 4b) Build StudentReport rows in memory
        student_reports = []
        for sid, sims in scores_map.items():
            mean_i = sum(sims) / len(sims)

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

            student_reports.append(
                StudentReport(
                    report=report,
                    submission_id=sid,
                    mean_similarity=mean_i,
                    z_score=z_val,
                    ci_lower=lo,
                    ci_upper=hi,
                )
            )

        # 4c) Bulk insert all StudentReports at once
        StudentReport.objects.bulk_create(student_reports)

        # 4d) Resolve professor via the course_instance on any Submission
        first_sub = (
            Submissions.objects.filter(assignment=assignment)
            .select_related("course_instance__professor")
            .first()
        )
        if not first_sub:
            raise Http404("No submissions found to determine professor.")
        professor = first_sub.course_instance.professor

        # 4e) Flag all similarity pairs for high-z students
        flags_created = flag_student_pairs(
            report=report,
            professor=professor,
            cutoff=1.282,
        )

        # 4f) Delete all older AssignmentReports for this assignment
        AssignmentReport.objects.filter(assignment=assignment).exclude(
            id=report.id
        ).delete()

        # 4g) Clean up orphaned StudentReports for deleted reports
        cleanup_old_student_reports(
            assignment=assignment,
            keep_report_id=report.id,
        )

    # 5) Return stats and summary to frontend
    return JsonResponse(
        {
            "report_id": report.id,
            "assignment_id": assignment.id,
            "students_analyzed": len(scores_map),
            "students_flagged": FlaggedStudents.objects.filter(
                professor=professor,
                similarity__assignment=assignment,
            ).values("student").distinct().count(),
            "flagged_similarity_rows": flags_created,
            "population_mu": mu,
            "population_sigma": sigma,
            "population_variance": variance,
        },
        json_dumps_params={"indent": 2},
    )


# -------------------------------
# Step-by-Step Example of generate_report
# -------------------------------
#
# Suppose for assignment #5 we have these similarity lists:
# scores_map = {
#     1: [30, 50],   # Student 1’s two comparisons (with 2 and 3)
#     2: [30, 20],   # Student 2’s comparisons (with 1 and 3)
#     3: [50, 20],   # Student 3’s comparisons (with 1 and 2)
# }
#
# And we have these students and their IDs:
#   Submission 1 → Student Alice
#   Submission 2 → Student Bob
#   Submission 3 → Student Carol
#
# 1) The user calls:
#      POST /api/cheating/5/generate_report/
#
# 2) Inside generate_report:
#    • Loads Assignment #5
#    • Calls get_all_scores_by_student() and receives the scores_map above
#
# 3) Compute population stats:
#      all_scores = [30, 50, 30, 20, 50, 20]
#      N_pop      = 6
#      μ          = (30+50+30+20+50+20)/6 = 33.33…
#      σ          = sqrt(variance) ≈ 12.91
#      Var        = σ² ≈ 166.7
#      N_pairs    = 6 // 2 = 3
#
# 4) Create AssignmentReport row:
#      AssignmentReport(
#        assignment=5,
#        mu=33.33,
#        sigma=12.91,
#        variance=166.7
#      )
#
# 5) For each student (sid → sims):
#
#    a) Student 1 (Alice): sims = [30, 50]
#       mean1 = 40.0
#       SE    = 12.91 / sqrt(2) * sqrt((3–2)/(3–1)) ≈ 6.45
#       z1    = (40.0 – 33.33) / 6.45 ≈ 1.04
#       CI    = 40 ± 1.96×6.45 ≈ [27.36, 52.64]
#
#    b) Student 2 (Bob): sims = [30, 20]
#       mean2 = 25.0
#       z2    = (25.0 – 33.33) / 6.45 ≈ –1.29
#       CI    = [12.36, 37.64]
#
#    c) Student 3 (Carol): sims = [50, 20]
#       mean3 = 35.0
#       z3    = (35.0 – 33.33) / 6.45 ≈ 0.26
#       CI    = [22.36, 47.64]
#
# 6) Save 3 StudentReport rows:
#      StudentReport(report=..., submission=1, mean_similarity=40.0, z_score=1.04, ...)
#      StudentReport(report=..., submission=2, mean_similarity=25.0, z_score=–1.29, ...)
#      StudentReport(report=..., submission=3, mean_similarity=35.0, z_score=0.26, ...)
#
# 7) Flagging phase (z > 1.282):
#      • None of the students exceed z = 1.282
#      • So no one is flagged, and the FlaggedStudents table stays empty
#
# 8) Example alternate case: if Alice had [60, 70] → mean=65 → z ≈ 2.0
#      • Alice would be flagged
#      • We'd lookup all SubmissionSimilarityPairs involving submission 1
#         (e.g. Alice–Bob and Alice–Carol)
#      • For each pair, we'd save:
#          FlaggedStudents(professor=..., student=Alice, similarity=pair, generative_ai=False)
#
# 9) JSON response looks like:
# {
#   "report_id": 17,
#   "assignment_id": 5,
#   "students_reported": 3,
#   "flags_created": 0,
#   "population_mu": 33.33,
#   "population_sigma": 12.91,
#   "population_variance": 166.7
# }
#
# Now the frontend can:
#   • Fetch report 17 to populate:
#       - forest plots (CI)
#       - z-score bar charts
#       - distribution histograms
#   • See who was flagged and why (via FlaggedStudents)
#   • Link flagged students by shared similarity pairs


def similarity_plot(request, assignment_id):
    """
    Render a vertical bar chart of flagged students’ z-scores as PNG.

    Pulls z-scores from StudentReport entries where z > cutoff.
    Student names resolved via Submissions and plotted on x-axis.
    """
    assignment = get_object_or_404(Assignments, pk=assignment_id)
    report = get_object_or_404(AssignmentReport, assignment=assignment)

    # Define threshold
    cutoff = 1.282

    # Fetch flagged students and cache them
    flagged_qs = StudentReport.objects.filter(report=report, z_score__gt=cutoff).only(
        "submission_id", "z_score"
    )

    if not flagged_qs.exists():
        raise Http404("No flagged students")

    # Bulk lookup submissions with related student info
    submission_ids = [sr.submission_id for sr in flagged_qs]
    sub_map = (
        Submissions.objects.filter(pk__in=submission_ids)
        .select_related("student")
        .in_bulk(field_name="pk")
    )

    # Assemble (student name, z-score)
    entries = []
    for sr in flagged_qs:
        submission = sub_map.get(sr.submission_id)
        if submission:
            name = f"{submission.student.first_name} {submission.student.last_name}"
        else:
            name = f"ID {sr.submission_id}"
        entries.append((name, sr.z_score))

    entries.sort(key=lambda x: x[1], reverse=True)
    names, zs = zip(*entries)

    fig, ax = plt.subplots(figsize=(max(8, len(names) * 0.5), 5))
    ax.bar(range(len(names)), zs, color="C1", edgecolor="black")

    for i, z in enumerate(zs):
        ax.text(i, z + 0.02, f"{z:.2f}", ha="center", va="bottom", fontsize=8)

    ax.axhline(
        cutoff,
        color="red",
        linestyle="--",
        label=f"Cutoff: z > {cutoff:.3f} (upper 90%)",
    )

    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Z-score of Mean Similarity")
    ax.set_title(f"Assignment {assignment_id}: Flagged Students")
    ax.legend(loc="upper right", fontsize=8)
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return HttpResponse(buf.read(), content_type="image/png")


def distribution_plot(request, assignment_id):
    """
    Render histogram of per-student mean similarities with Normal overlay.

    Uses StudentReport for means and AssignmentReport for population stats.
    """
    assignment = get_object_or_404(Assignments, pk=assignment_id)
    report = get_object_or_404(AssignmentReport, assignment=assignment)

    srs = list(
        StudentReport.objects.filter(report=report).only(
            "submission_id", "mean_similarity"
        )
    )
    if not srs:
        raise Http404("No student data to plot")

    means = [sr.mean_similarity for sr in srs]

    # Get population values
    mu = report.mu
    sigma = report.sigma
    var = report.variance

    # Fetch all scores once to avoid recomputing
    scores_map = get_all_scores_by_student(assignment)

    # Compute average sample size
    total_comparisons = sum(len(scores_map.get(sr.submission_id, [])) for sr in srs)
    n_avg = total_comparisons / len(means)
    se = sigma / (n_avg**0.5)

    fig, ax = plt.subplots(figsize=(8, 4))
    counts, bins, _ = ax.hist(
        means,
        bins=30,
        density=True,
        alpha=0.6,
        color="C0",
        edgecolor="black",
    )

    xs = [bins[0] + i * (bins[-1] - bins[0]) / 200 for i in range(201)]
    pdf = [
        (1 / (se * (2 * math.pi) ** 0.5)) * math.exp(-0.5 * ((x - mu) / se) ** 2)
        for x in xs
    ]
    ax.plot(xs, pdf, "k--", label="Normal PDF (CLT)")

    text = f"μ = {mu:.2f}\nσ = {sigma:.2f}\nVar = {var:.2f}"
    ax.text(
        0.98,
        0.95,
        text,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        bbox=dict(facecolor="white", alpha=0.7, boxstyle="round,pad=0.3"),
    )

    ax.set_xlabel("Per‑student Mean Similarity (%)")
    ax.set_ylabel("Density")
    ax.set_title(f"Assignment {assignment_id}: Distribution")
    ax.legend(loc="upper left", fontsize=8)
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return HttpResponse(buf.read(), content_type="image/png")


def similarity_interval_plot(request, assignment_id):
    """
    Render forest plot of 95% CI for flagged students' mean similarities.

    Plots mean ± CI, labels with z-scores from StudentReport.
    """
    assignment = get_object_or_404(Assignments, pk=assignment_id)
    report = get_object_or_404(AssignmentReport, assignment=assignment)

    cutoff = 1.282
    srs = list(
        StudentReport.objects.filter(report=report, z_score__gt=cutoff).only(
            "submission_id", "mean_similarity", "ci_lower", "ci_upper", "z_score"
        )
    )
    if not srs:
        raise Http404("No flagged students to plot")

    # Resolve all names via bulk lookup
    submission_ids = [sr.submission_id for sr in srs]
    sub_map = (
        Submissions.objects.filter(pk__in=submission_ids)
        .select_related("student")
        .in_bulk(field_name="pk")
    )

    data = []
    for sr in srs:
        submission = sub_map.get(sr.submission_id)
        if submission:
            name = f"{submission.student.first_name} {submission.student.last_name}"
        else:
            name = f"ID {sr.submission_id}"
        data.append((name, sr.mean_similarity, sr.ci_lower, sr.ci_upper, sr.z_score))

    data.sort(key=lambda x: x[1], reverse=True)
    names, means, lowers, uppers, zs = zip(*data)

    left_errs = [m - lo for m, lo in zip(means, lowers)]
    right_errs = [hi - m for hi, m in zip(uppers, means)]

    fig, ax = plt.subplots(figsize=(6, max(4, len(names) * 0.4)))
    ax.errorbar(
        means,
        range(len(names)),
        xerr=[left_errs, right_errs],
        fmt="o",
        capsize=4,
        color="C1",
    )

    ax.axvline(
        report.mu,
        color="grey",
        linestyle="--",
        label=f"Population μ = {report.mu:.1f}%",
    )

    for i, z in enumerate(zs):
        ax.text(uppers[i] + 0.5, i, f"z={z:.2f}", va="center", fontsize=8)

    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=8)
    ax.invert_yaxis()

    ax.set_xlabel("Mean Similarity (%) with 95% CI")
    ax.set_title(f"Assignment {assignment_id}: Flagged CI")
    ax.legend(loc="lower right", fontsize=8)
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return HttpResponse(buf.read(), content_type="image/png")
