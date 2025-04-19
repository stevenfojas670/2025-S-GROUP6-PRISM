"""Views for the Cheating app with enhanced filtering, ordering, search, and pagination."""

from rest_framework import filters, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from prism_backend.mixins import CachedViewMixin

from .models import (
    CheatingGroups,
    CheatingGroupMembers,
    ConfirmedCheaters,
    FlaggedStudents,
    SubmissionSimilarityPairs,
    LongitudinalCheatingGroups,
    LongitudinalCheatingGroupMembers,
    LongitudinalCheatingGroupInstances,
)
from assignments.models import Submissions
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

from io import BytesIO
import math
import io
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404

# Use a non-interactive backend for rendering
import matplotlib
matplotlib.use("Agg")

from matplotlib import pyplot as plt

from assignments.models import Assignments
from .utils.similarity_analysis import (
    compute_population_stats,
    compute_student_confidence_interval,
    compute_student_z_score,
    get_all_scores_by_student,
)


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

def similarity_plot(request, assignment_id):
    """
    Render a vertical bar chart of flagged students’ z-scores as PNG.

    • Only students with z > cutoff are plotted.
    • Bars are annotated with their z-value.
    • Legend shows z cutoff and corresponding tail probability.
    """
    # 1) Fetch the assignment or 404
    assignment = get_object_or_404(Assignments, pk=assignment_id)

    # 2) Build mapping: submission_id -> list of similarity percentages
    scores_map = get_all_scores_by_student(assignment)
    if not scores_map:
        raise Http404(f"No similarity data for assignment {assignment_id}")

    # 3) Compute population mean (mu) and std dev (sigma)
    mu, sigma = compute_population_stats(scores_map)

    # 4) Compute total unique comparisons N for FPC correction
    total_values = sum(len(lst) for lst in scores_map.values()) // 2

    # 5) Fetch Submissions to map IDs -> student names
    subs = (
        Submissions.objects
        .filter(pk__in=scores_map)
        .select_related("student")
    )
    name_map = {
        sub.pk: f"{sub.student.first_name} {sub.student.last_name}"
        for sub in subs
    }

    # 6) Compute each student's z-score
    entries = []
    for sid, sims in scores_map.items():
        _, z_val = compute_student_z_score(
            scores=sims,
            mu=mu,
            sigma=sigma,
            use_fpc=True,
            population_size=total_values,
        )
        # resolve display name or fallback to ID
        name = name_map.get(sid, f"ID {sid}")
        entries.append((name, z_val))

    # 7) Define cutoff for one-sided 90% → z > 1.282
    cutoff = 1.282
    tail_prob = 0.10  # P(Z > cutoff) under H0

    # 8) Filter only flagged students (z > cutoff)
    flagged = [(n, z) for n, z in entries if z > cutoff]
    if not flagged:
        raise Http404("No students exceed the z-score cutoff")

    # 9) Sort flagged by descending z
    flagged.sort(key=lambda x: x[1], reverse=True)
    names, zs = zip(*flagged)

    # 10) Prepare bar colors
    colors = ["C1"] * len(zs)

    # 11) Create figure sized to number of flags
    fig, ax = plt.subplots(
        figsize=(max(8, len(names) * 0.5), 5)
    )

    # 12) Draw vertical bars
    bars = ax.bar(
        range(len(names)),
        zs,
        color=colors,
        edgecolor="black",
    )

    # 13) Annotate each bar with its z-value
    for idx, z in enumerate(zs):
        ax.text(
            idx,               # x position
            z + 0.02,          # just above bar
            f"{z:.2f}",        # z to 2 decimals
            ha="center",
            va="bottom",
            fontsize=8,
        )

    # 14) Draw horizontal cutoff line, include tail prob in legend
    ax.axhline(
        y=cutoff,
        color="red",
        linestyle="--",
        label=(
            f"Cutoff: z > {cutoff:.3f} "
            f"(upper {100*(1-tail_prob):.0f}th percentile)"
        ),
    )

    # 15) Configure x-axis with student names, rotate labels
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(
        names,
        rotation=45,
        ha="right",
        fontsize=8,
    )

    # 16) Label axes and title
    ax.set_ylabel("Z-score of Mean Similarity")
    ax.set_title(f"Assignment {assignment_id}: Flagged Students")
    ax.legend(loc="upper right", fontsize=8)

    # 17) Tight layout for rotated labels
    plt.tight_layout()

    # 18) Render to PNG buffer
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    # 19) Return PNG in HTTP response
    return HttpResponse(
        buf.read(), content_type="image/png"
    )

def distribution_plot(request, assignment_id):
    """
    Render a histogram of per‑student mean similarities with a Normal
    overlay, and annotate μ, σ, and variance. Returns PNG.

    Steps:
      1) Fetch assignment or 404.
      2) Build submission_id → [scores].
      3) Compute population μ, σ, variance.
      4) Compute per‑student means.
      5) Draw histogram of those means.
      6) Overlay Normal PDF (CLT) with σ/√n.
      7) Annotate text box with μ, σ, variance.
      8) Stream PNG response.
    """
    # 1) Retrieve the Assignment or raise 404
    assignment = get_object_or_404(Assignments, pk=assignment_id)

    # 2) Get all similarity scores per submission
    scores_map = get_all_scores_by_student(assignment)
    if not scores_map:
        raise Http404(f"No similarity data for assignment {assignment_id}")

    # 3) Compute population statistics: mean (mu), std dev (sigma),
    #    and variance (var = sigma^2)
    mu, sigma = compute_population_stats(scores_map)
    var = sigma * sigma

    # 4) Compute per-student sample means
    means = []
    for sims in scores_map.values():
        # each sims is a list of percentages
        means.append(sum(sims) / len(sims))

    # 5) Set up figure and axis for histogram
    fig, ax = plt.subplots(figsize=(8, 4))

    # 6) Draw histogram of means, density=True for PDF scaling
    counts, bins, _ = ax.hist(
        means,
        bins=30,
        density=True,
        alpha=0.6,
        color="C0",
        edgecolor="black",
    )

    # 7) Overlay Normal PDF using CLT: std_error = sigma / sqrt(n)
    #    We take n as the average sample size
    n_avg = sum(len(sims) for sims in scores_map.values()) / len(means)
    se = sigma / math.sqrt(n_avg)
    # prepare x-axis for PDF
    x_min, x_max = min(bins), max(bins)
    x_vals = [x_min + i*(x_max-x_min)/200 for i in range(201)]
    # compute PDF values
    pdf = [
        (1 / (se * math.sqrt(2 * math.pi)))
        * math.exp(-((x - mu) ** 2) / (2 * se * se))
        for x in x_vals
    ]
    # plot PDF curve
    ax.plot(x_vals, pdf, "k--", label="Normal PDF (CLT)")

    # 8) Annotate with text box showing μ, σ, variance
    textstr = "\n".join([
        f"μ = {mu:.2f}",
        f"σ = {sigma:.2f}",
        f"Var = {var:.2f}"
    ])
    # place in upper right corner of plot
    ax.text(
        0.98,
        0.95,
        textstr,
        transform=ax.transAxes,
        fontsize=9,
        verticalalignment="top",
        horizontalalignment="right",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                  alpha=0.7)
    )

    # 9) Labels and legend
    ax.set_xlabel("Per‑student Mean Similarity (%)")
    ax.set_ylabel("Density")
    ax.set_title(f"Assignment {assignment_id}: Distribution of Means")
    ax.legend(loc="upper left", fontsize=8)

    # 10) Layout and render to PNG buffer
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    # 11) Return PNG image in HTTP response
    return HttpResponse(buf.read(), content_type="image/png")