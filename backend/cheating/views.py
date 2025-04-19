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

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404

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
    Render a per-student similarity error-bar plot as a PNG image.

    Fetches all similarity scores for each student in the assignment,
    computes population statistics, per-student z-scores and 95% CIs,
    then draws an error-bar plot (mean ± CI) with a horizontal line
    at the population mean.
    """
    # 1) Retrieve the Assignment object or return 404 if not found
    assignment = get_object_or_404(Assignments, pk=assignment_id)

    # 2) Build a dict of submission_id -> [similarity percentages...]
    scores_map = get_all_scores_by_student(assignment)
    if not scores_map:
        # If no data exists for this assignment, signal "Not Found"
        raise Http404(f"No similarity data for assignment {assignment_id}")

    # 3) Compute overall population mean (mu) and std dev (sigma)
    mu, sigma = compute_population_stats(scores_map)

    # 4) Determine total unique comparisons N for finite-pop correction (FPC)
    #    Each pair was counted twice (once per student), so divide by 2
    total_values = sum(len(v) for v in scores_map.values()) // 2

    # 5) Prepare lists for plotting
    students = []  # x-axis: submission (student) IDs
    means = []  # y-axis: per-student mean similarity
    lower_err = []  # lower error bar lengths
    upper_err = []  # upper error bar lengths

    # 6) Iterate in sorted order for consistent x-axis
    for sid, sims in sorted(scores_map.items()):
        # 6.1) Compute sample mean and z-score using our helper
        mean_i, z_i = compute_student_z_score(
            scores=sims,
            mu=mu,
            sigma=sigma,
            use_fpc=True,
            population_size=total_values,
        )
        # 6.2) Compute 95% confidence interval using helper
        ci_low, ci_high = compute_student_confidence_interval(
            scores=sims,
            sigma=sigma,
            conf_level=0.95,
            use_fpc=True,
            population_size=total_values,
        )
        # 6.3) Store values: mean and asymmetric error distances
        students.append(sid)
        means.append(mean_i)
        lower_err.append(mean_i - ci_low)
        upper_err.append(ci_high - mean_i)

    # 7) Create the matplotlib figure and axis
    fig, ax = plt.subplots(figsize=(8, 4))

    # 7.1) Plot error bars: fmt='o' makes circular markers
    ax.errorbar(
        students,
        means,
        yerr=[lower_err, upper_err],
        fmt="o",
        capsize=5,
        label="Mean ± 95% CI",
    )

    # 7.2) Add a horizontal line at the population mean
    ax.axhline(
        y=mu,
        color="red",
        linestyle="--",
        label=f"Population μ = {mu:.1f}",
    )

    # 7.3) Label axes and title
    ax.set_xlabel("Submission ID")
    ax.set_ylabel("Mean Similarity (%)")
    ax.set_title(f"Assignment {assignment_id}: Similarity by Student")

    # 7.4) Show legend and adjust layout
    ax.legend()
    fig.tight_layout()

    # 8) Render figure to PNG in memory
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    plt.close(fig)  # free memory
    buffer.seek(0)

    # 9) Return image as HTTP response
    return HttpResponse(buffer.read(), content_type="image/png")
