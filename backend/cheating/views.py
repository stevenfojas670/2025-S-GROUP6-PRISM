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


def flag_student_pairs(report, professor, cutoff=1.282):
    """
    Flag all similarity pairs involving students with z > cutoff.

    For each high‑z student, we gather all SubmissionSimilarityPairs
    for that student’s submission on this assignment. Then we insert
    one FlaggedStudents row per pair, with generative_ai=False.

    Args:
        report (AssignmentReport): the report containing student z-scores.
        professor (Professors): the professor who flagged the students.
        cutoff (float): z-score threshold to flag (default = 1.282 for 90%).

    Returns:
        int: number of FlaggedStudents created
    """
    created_rows = []

    # 1) Get all students with z-score > cutoff
    suspects = report.student_reports.filter(z_score__gt=cutoff)

    for sr in suspects:
        submission = sr.submission
        student = submission.student

        # 2) Get all pairwise similarities this student is involved in
        pairs = SubmissionSimilarityPairs.objects.filter(
            assignment=report.assignment
        ).filter(Q(submission_id_1=submission) | Q(submission_id_2=submission))

        # 3) Prepare FlaggedStudents objects (one per similarity pair)
        for pair in pairs:
            created_rows.append(
                FlaggedStudents(
                    professor=professor,
                    student=student,
                    similarity=pair,
                    generative_ai=False,
                )
            )

    # 4) Avoid duplicates with bulk insert + ignore_conflicts=True
    inserted = FlaggedStudents.objects.bulk_create(
        created_rows,
        ignore_conflicts=True,  # respects unique_together
    )

    return len(inserted)


def generate_report(request, assignment_id):
    """
    Compute & persist an AssignmentReport and StudentReports.

    Then flag pairs based on z-score threshold.
    Steps:
      1) Fetch Assignment or 404.
      2) Gather per-student similarity percentages.
      3) Compute population μ, σ, variance, and N_pairs.
      4) In transaction:
         a) create AssignmentReport
         b) bulk create StudentReports
         c) call flag_student_pairs(report, professor, cutoff)
      5) Return JSON summary.
    """
    # 1) Fetch the assignment or raise 404
    assignment = get_object_or_404(Assignments, pk=assignment_id)

    # 2) Build dictionary: submission_id -> list of similarity scores
    scores_map = get_all_scores_by_student(assignment)
    if not scores_map:
        raise Http404("No similarity data available for this assignment.")

    # 3) Compute population statistics
    mu, sigma = compute_population_stats(scores_map)
    variance = sigma**2
    total_pairs = sum(len(v) for v in scores_map.values()) // 2

    # 4) Transaction block for all database writes
    with transaction.atomic():
        # 4a) Create one AssignmentReport row
        report = AssignmentReport.objects.create(
            assignment=assignment,
            mu=mu,
            sigma=sigma,
            variance=variance,
        )

        # 4b) Build all StudentReports in memory
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

        # Insert all reports at once
        StudentReport.objects.bulk_create(student_reports)

        # 4c) Grab any submission to find the professor via course_instance
        first_sub = (
            Submissions.objects.filter(assignment=assignment)
            .select_related("course_instance__professor")
            .first()
        )
        if not first_sub:
            raise Http404("Could not determine professor from submissions.")
        professor = first_sub.course_instance.professor

        # Call helper to flag similar pairs for students with high z-score
        flags_created = flag_student_pairs(
            report=report,
            professor=professor,
            cutoff=1.282,
        )
        # Cleanup: ensure only this report remains
        AssignmentReport.objects.filter(assignment=assignment).exclude(
            id=report.id
        ).delete()

    # 5) Return JSON summary
    return JsonResponse(
        {
            "report_id": report.id,
            "assignment_id": assignment.id,
            "students_reported": len(scores_map),
            "flags_created": flags_created,
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

    Reads z_scores from StudentReport where z_score > cutoff, and
    labels by student name.  Returns an HTTPResponse with image/png.
    """
    # 1) Load Assignment or 404
    assignment = get_object_or_404(Assignments, pk=assignment_id)

    # 2) Get the corresponding AssignmentReport or 404
    report = get_object_or_404(AssignmentReport, assignment=assignment)

    # 3) Fetch all StudentReport entries for this report with z>cutoff
    cutoff = 1.282
    flagged_qs = StudentReport.objects.filter(report=report, z_score__gt=cutoff)

    if not flagged_qs.exists():
        raise Http404("No students exceed z-score cutoff")

    # 4) Build list of (name, z_score)
    subs = Submissions.objects.filter(
        pk__in=[sr.submission_id for sr in flagged_qs]
    ).select_related("student")

    name_map = {
        sub.pk: f"{sub.student.first_name} {sub.student.last_name}" for sub in subs
    }

    entries = []
    for sr in flagged_qs:
        name = name_map.get(sr.submission_id, f"ID {sr.submission_id}")
        entries.append((name, sr.z_score))

    # 5) Sort by descending z_score
    entries.sort(key=lambda x: x[1], reverse=True)
    names, zs = zip(*entries)

    # 6) Prepare plot
    fig, ax = plt.subplots(figsize=(max(8, len(names) * 0.5), 5))

    ax.bar(range(len(names)), zs, color="C1", edgecolor="black")

    # 7) Annotate bars with z_value
    for i, z in enumerate(zs):
        ax.text(i, z + 0.02, f"{z:.2f}", ha="center", va="bottom", fontsize=8)

    # 8) Draw cutoff line + legend
    tail_pct = 90  # upper 90th percentile
    ax.axhline(
        cutoff,
        color="red",
        linestyle="--",
        label=f"Cutoff: z > {cutoff:.3f} (upper {tail_pct}%)",
    )

    # 9) X-axis labels
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=8)

    # 10) Final styling
    ax.set_ylabel("Z-score of Mean Similarity")
    ax.set_title(f"Assignment {assignment_id}: Flagged Students")
    ax.legend(loc="upper right", fontsize=8)
    plt.tight_layout()

    # 11) Render to PNG
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    return HttpResponse(buf.read(), content_type="image/png")


def distribution_plot(request, assignment_id):
    """Render histogram of per-student means with Normal overlay.

    Reads μ, σ, variance from AssignmentReport and sample means
    from StudentReport. Returns PNG.
    """
    # 1) Load Assignment & Report
    assignment = get_object_or_404(Assignments, pk=assignment_id)
    report = get_object_or_404(AssignmentReport, assignment=assignment)

    # 2) Pull all StudentReport.means for this report
    srs = StudentReport.objects.filter(report=report)
    if not srs.exists():
        raise Http404("No student data to plot")

    means = [sr.mean_similarity for sr in srs]

    # 3) Extract population stats
    mu = report.mu
    sigma = report.sigma
    variance = report.variance

    # 4) Build histogram
    fig, ax = plt.subplots(figsize=(8, 4))
    counts, bins, _ = ax.hist(
        means,
        bins=30,
        density=True,
        alpha=0.6,
        color="C0",
        edgecolor="black",
    )

    # 5) Overlay Normal PDF via CLT: se = sigma/√n_avg
    n_avg = sum(
        len(get_all_scores_by_student(assignment).get(sr.submission_id, []))
        for sr in srs
    ) / len(means)
    se = sigma / (n_avg**0.5)

    xs = [bins[0] + i * (bins[-1] - bins[0]) / 200 for i in range(201)]
    pdf = [
        (1 / (se * (2 * math.pi) ** 0.5)) * math.exp(-0.5 * ((x - mu) / se) ** 2)
        for x in xs
    ]
    ax.plot(xs, pdf, "k--", label="Normal PDF (CLT)")

    # 6) Annotate μ, σ, Var
    text = f"μ = {mu:.2f}\nσ = {sigma:.2f}\nVar = {variance:.2f}"
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

    # 7) Labels & legend
    ax.set_xlabel("Per‑student Mean Similarity (%)")
    ax.set_ylabel("Density")
    ax.set_title(f"Assignment {assignment_id}: Distribution")
    ax.legend(loc="upper left", fontsize=8)
    plt.tight_layout()

    # 8) Render PNG
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    return HttpResponse(buf.read(), content_type="image/png")


def similarity_interval_plot(request, assignment_id):
    """
    Render horizontal error bars (95% CI) for flagged students.

    1) Reads μ, σ from AssignmentReport.
    Reads CI bounds from StudentReport where z_score > cutoff.
    """
    # 1) Load Assignment & Report
    assignment = get_object_or_404(Assignments, pk=assignment_id)
    report = get_object_or_404(AssignmentReport, assignment=assignment)

    # 2) Filter StudentReports by z_score > cutoff
    cutoff = 1.282
    srs = StudentReport.objects.filter(report=report, z_score__gt=cutoff)
    if not srs.exists():
        raise Http404("No flagged students to plot CI")

    # 3) Build list of (name, mean, lower, upper)
    subs = Submissions.objects.filter(
        pk__in=[sr.submission_id for sr in srs]
    ).select_related("student")
    name_map = {
        sub.pk: f"{sub.student.first_name} {sub.student.last_name}" for sub in subs
    }

    data = []
    for sr in srs:
        name = name_map.get(sr.submission_id, f"ID {sr.submission_id}")
        data.append((name, sr.mean_similarity, sr.ci_lower, sr.ci_upper))

    # 4) Sort by mean descending
    data.sort(key=lambda x: x[1], reverse=True)
    names, means, lowers, uppers = zip(*data)

    # 5) Compute left/right error lengths
    left_errs = [m - lo for m, lo in zip(means, lowers)]
    right_errs = [hi - m for hi, m in zip(uppers, means)]

    # 6) Plot horizontal error bars
    fig, ax = plt.subplots(figsize=(6, max(4, len(names) * 0.4)))
    ax.errorbar(
        means,
        range(len(names)),
        xerr=[left_errs, right_errs],
        fmt="o",
        capsize=4,
        color="C1",
    )

    # 7) Vertical line at μ
    ax.axvline(
        report.mu,
        color="grey",
        linestyle="--",
        label=f"Population μ = {report.mu:.1f}%",
    )

    # 8) Annotate each bar with its z_score
    for idx, sr in enumerate(srs.order_by("-mean_similarity")):
        z = sr.z_score
        ax.text(uppers[idx] + 0.5, idx, f"z={z:.2f}", va="center", fontsize=8)

    # 9) Y-axis labels & invert
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=8)
    ax.invert_yaxis()

    # 10) Labels, title, legend
    ax.set_xlabel("Mean Similarity (%) with 95% CI")
    ax.set_title(f"Assignment {assignment_id}: Flagged CI")
    ax.legend(loc="lower right", fontsize=8)
    plt.tight_layout()

    # 11) Render PNG
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    return HttpResponse(buf.read(), content_type="image/png")
