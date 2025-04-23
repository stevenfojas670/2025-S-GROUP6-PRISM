"""Views for the Cheating app with enhanced filtering, ordering, search, and pagination."""

from django.db import connection
import io
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from sklearn.cluster import KMeans
from sklearn.discriminant_analysis import StandardScaler
from courses.models import CourseCatalog, Semester
import matplotlib
from matplotlib import pyplot as plt
import time
import numpy as np
from django.db import transaction
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from prism_backend.mixins import CachedViewMixin
from django.views.decorators.http import require_POST
from assignments.models import Assignments, Submissions
from scipy.spatial import ConvexHull, QhullError
from sklearn.decomposition import PCA
from matplotlib.patches import Circle
from .services import (
    bulk_recompute_semester_profiles,
    run_kmeans_for_course_semester,
)
from .services import generate_report as generate_report_service
from django.views.decorators.http import require_GET
from .models import (
    CheatingGroups,
    CheatingGroupMembers,
    ConfirmedCheaters,
    FlaggedStudentPair,
    FlaggedStudents,
    PairFlagStat,
    SubmissionSimilarityPairs,
    LongitudinalCheatingGroups,
    LongitudinalCheatingGroupMembers,
    LongitudinalCheatingGroupInstances,
    AssignmentReport,
    StudentReport,
    StudentSemesterProfile,
)
from assignments.models import Assignments

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
    get_all_scores_by_student,
    update_all_pair_stats,
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


def similarity_plot(request, assignment_id):
    """
    Render a vertical bar chart of flagged students’ z-scores as PNG.

    Pulls z-scores from StudentReport entries where z > cutoff.
    Student names resolved via Submissions and plotted on x-axis.
    """
    # here I’m retrieving the Assignment and its latest report to get the z-scores
    assignment = get_object_or_404(Assignments, pk=assignment_id)
    report = get_object_or_404(AssignmentReport, assignment=assignment)

    # this is our z-score cutoff — anything above this is considered suspicious
    # I’m using 1.282 for the upper 90% threshold (z > 1.282)
    # i am using 2.0 for the upper 95% threshold (z > 2.0)
    # ill have to selct one of the 2
    cutoff = 2.0

    # now I’m pulling all students with z-scores above the threshold from the latest report
    # I’m also caching only what I need to minimize query overhead
    flagged_qs = StudentReport.objects.filter(report=report, z_score__gt=cutoff).only(
        "submission_id", "z_score"
    )

    # if no one is above threshold, we bail early with a 404
    if not flagged_qs.exists():
        raise Http404("No flagged students")

    # here I’m resolving all submission IDs to fetch student names in one go
    # using in_bulk for faster lookup instead of one query per student
    submission_ids = [sr.submission_id for sr in flagged_qs]
    sub_map = (
        Submissions.objects.filter(pk__in=submission_ids)
        .select_related("student")
        .in_bulk(field_name="pk")
    )

    # now we pair student names with their z-scores to build the bar chart entries
    entries = []
    for sr in flagged_qs:
        submission = sub_map.get(sr.submission_id)
        if submission:
            name = f"{submission.student.first_name} {submission.student.last_name}"
        else:
            name = f"ID {sr.submission_id}"
        entries.append((name, sr.z_score))

    # I want to display from highest z down, so let’s sort by z descending
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
    # load the assignment and associated stats report
    assignment = get_object_or_404(Assignments, pk=assignment_id)
    report = get_object_or_404(AssignmentReport, assignment=assignment)

    # pulling all student-level stats from the report
    srs = list(
        StudentReport.objects.filter(report=report).only(
            "submission_id", "mean_similarity"
        )
    )
    if not srs:
        raise Http404("No student data to plot")

    # extract the mean similarities from the queryset for histogram plotting
    means = [sr.mean_similarity for sr in srs]

    # we need the population-level stats to overlay the normal curve
    mu = report.mu
    sigma = report.sigma
    var = report.variance

    # I’ll reuse cached similarity scores to compute average sample size (used for SE)
    scores_map = get_all_scores_by_student(assignment)

    # compute average number of comparisons per student to estimate SE (CLT)
    total_comparisons = sum(len(scores_map.get(sr.submission_id, [])) for sr in srs)
    n_avg = total_comparisons / len(means)
    se = sigma / (n_avg**0.5)  # this is the SE used in normal overlay

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
    # we start off by resolving the assignment and its current report
    assignment = get_object_or_404(Assignments, pk=assignment_id)
    report = get_object_or_404(AssignmentReport, assignment=assignment)

    # students above this z-score threshold will be shown in the forest plot
    cutoff = 2.0
    srs = list(
        StudentReport.objects.filter(report=report, z_score__gt=cutoff).only(
            "submission_id", "mean_similarity", "ci_lower", "ci_upper", "z_score"
        )
    )
    if not srs:
        raise Http404("No flagged students to plot")

    # I want names to show up instead of submission IDs, so I bulk-fetch student info
    submission_ids = [sr.submission_id for sr in srs]
    sub_map = (
        Submissions.objects.filter(pk__in=submission_ids)
        .select_related("student")
        .in_bulk(field_name="pk")
    )

    # building the final display data: name, mean sim, CI bounds, and z-score
    data = []
    for sr in srs:
        submission = sub_map.get(sr.submission_id)
        if submission:
            name = f"{submission.student.first_name} {submission.student.last_name}"
        else:
            name = f"ID {sr.submission_id}"
        data.append((name, sr.mean_similarity, sr.ci_lower, sr.ci_upper, sr.z_score))

    # I want top cheaters first, so I sort by mean similarity in descending order
    data.sort(key=lambda x: x[1], reverse=True)
    names, means, lowers, uppers, zs = zip(*data)

    # here I’m computing the left and right error bars (distance from mean to CI)
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


@require_GET
def kmeans_clusters_plot(request, course_id, semester_id):
    """
    2D PCA plot of K‑Means clusters for students, colored & labeled:
      • convex‐hull if ≥3 points
      • circle if 1–2 points
      • extremes (outliers) annotated

      Low Intensity = cluster with lowest avg_z
      High Intensity = cluster with highest avg_z
      Medium Intensity = everything in between
    """
    # — 1) Load profiles + student names
    qs = StudentSemesterProfile.objects.filter(
        course_catalog_id=course_id,
        semester_id=semester_id,
    ).select_related("student")
    if not qs.exists():
        raise Http404("No data for that course & semester.")

    # — 2) Extract raw vectors, labels, names
    #    each feature_vector is now length=7
    X_raw = np.vstack([p.feature_vector for p in qs])  # (n_students, 7)
    labels = np.array([p.cluster_label for p in qs])
    names = [f"{p.student.first_name} {p.student.last_name}" for p in qs]

    # — 3) Standardize + PCA → 2D
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)
    pca = PCA(n_components=2, random_state=42)
    XY = pca.fit_transform(X_scaled)
    dim1, dim2 = XY[:, 0], XY[:, 1]
    var1 = pca.explained_variance_ratio_[0] * 100
    var2 = pca.explained_variance_ratio_[1] * 100

    # — 4) Compute each cluster’s centroid avg_z (feature #0) WITHOUT re‑fitting
    unique_lbls = sorted(set(labels))
    centroids = {lbl: X_scaled[labels == lbl].mean(axis=0) for lbl in unique_lbls}
    avg_z = {lbl: centroids[lbl][0] for lbl in unique_lbls}

    # figure out low‐z vs high‐z clusters
    min_lbl = min(unique_lbls, key=lambda l: avg_z[l])
    max_lbl = max(unique_lbls, key=lambda l: avg_z[l])

    # — 5) Build style maps
    color_map, legend_map, marker_map = {}, {}, {}
    for lbl in unique_lbls:
        cnt = int((labels == lbl).sum())
        if lbl == min_lbl:
            color_map[lbl], marker_map[lbl] = "green", "o"
            legend_map[lbl] = f"Low Intensity (n={cnt})"
        elif lbl == max_lbl:
            color_map[lbl], marker_map[lbl] = "red", "^"
            legend_map[lbl] = f"High Intensity (n={cnt})"
        else:
            color_map[lbl], marker_map[lbl] = "gold", "s"
            legend_map[lbl] = f"Medium Intensity (n={cnt})"

    # — 6) Plot each cluster
    fig, ax = plt.subplots(figsize=(10, 8))
    for lbl in unique_lbls:
        xi = dim1[labels == lbl]
        yi = dim2[labels == lbl]

        ax.scatter(
            xi,
            yi,
            c=color_map[lbl],
            marker=marker_map[lbl],
            s=100,
            edgecolor="k",
            alpha=0.8,
            label=legend_map[lbl],
        )

        pts = list(zip(xi, yi))
        if len(pts) >= 3:
            try:
                hull = ConvexHull(pts)
                hull_pts = [pts[i] for i in hull.vertices]
                hx, hy = zip(*hull_pts)
                ax.fill(hx, hy, color=color_map[lbl], alpha=0.2)
            except QhullError:
                pass
        elif pts:
            cx, cy = np.mean(xi), np.mean(yi)
            dists = np.hypot(xi - cx, yi - cy)
            r = (dists.max() if dists.size else 0.5) * 1.5
            circ = Circle(
                (cx, cy),
                radius=r or 0.5,
                color=color_map[lbl],
                alpha=0.2,
                edgecolor=None,
            )
            ax.add_patch(circ)

    # — 7) Annotate only the extreme outliers
    x_lo, x_hi = np.percentile(dim1, [10, 90])
    y_lo, y_hi = np.percentile(dim2, [10, 90])
    for x, y, name in zip(dim1, dim2, names):
        if not (x_lo < x < x_hi and y_lo < y < y_hi):
            ax.annotate(
                name,
                xy=(x, y),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=8,
                alpha=0.9,
            )

    # — 8) Final styling & title
    course = get_object_or_404(CourseCatalog, pk=course_id)
    semester = get_object_or_404(Semester, pk=semester_id)
    ax.set_xlabel(f"Dim1 ({var1:.1f}% variance)", fontsize=12)
    ax.set_ylabel(f"Dim2 ({var2:.1f}% variance)", fontsize=12)
    ax.set_title(f"K‑Means Clusters → {course} — {semester}", fontsize=14, pad=15)
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.7)
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), title="Student Groups")
    plt.tight_layout()

    # — 9) Return as PNG
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return HttpResponse(buf.read(), content_type="image/png")


def run_kmeans_for_pair_stats(
    course_id,
    semester_id,
    student_km=None,
    n_clusters=6,
    random_state=0,
    b_refs=10,
    red_threshold=30,
    max_multiplier=2,
):
    """
    1) (optional) we can use student_km to get per-student labels
    2) build & weight a 5-dim feature matrix for each pair
    3) standardize, gap-statistic → pick best_k
    4) fit & find 'red' cluster; if red_size > red_threshold, clear FlaggedStudentPair
       else create FlaggedStudentPair records for every pair in 'red'
    5) remap PairFlagStat.kmeans_label
    """
    start_ts = time.time()

    # 1) load pair stats
    pairs = list(
        PairFlagStat.objects.filter(
            course_catalog_id=course_id,
            semester_id=semester_id,
        )
    )
    if not pairs:
        raise Http404("No pair stats available")

    # student→label map
    if student_km:
        ids, labs = student_km._fit_student_ids_, student_km.labels_
        student_lbl = dict(zip(ids, labs))
    else:
        qs = StudentSemesterProfile.objects.filter(
            course_catalog_id=course_id,
            semester_id=semester_id,
        ).only("student_id", "cluster_label")
        student_lbl = {p.student_id: (p.cluster_label or 0) for p in qs}

    # 2) assemble feature matrix
    X_raw = np.zeros((len(pairs), 5), dtype=float)
    for i, ps in enumerate(pairs):
        X_raw[i, 0] = ps.mean_z_score**9
        X_raw[i, 1] = ps.max_z_score**5
        X_raw[i, 2] = ps.mean_similarity**2
        X_raw[i, 3] = ps.proportion * 100.0
        la = student_lbl.get(ps.student_a_id, 0)
        lb = student_lbl.get(ps.student_b_id, 0)
        X_raw[i, 4] = la + lb

    # standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    # 3) gap-statistic to choose best_k
    def _disp(data, labels, centers):
        return sum(np.sum((data[labels == i] - c) ** 2) for i, c in enumerate(centers))

    mins, maxs = X_scaled.min(0), X_scaled.max(0)
    best_k, best_gap = None, -np.inf

    for k in range(2, n_clusters + 1):
        km_ref = KMeans(n_clusters=k, random_state=random_state).fit(X_scaled)
        Wk = _disp(X_scaled, km_ref.labels_, km_ref.cluster_centers_)
        logWk = np.log(Wk)

        ref_logs = []
        for _ in range(b_refs):
            Xb = np.random.uniform(mins, maxs, size=X_scaled.shape)
            kmb = KMeans(n_clusters=k, random_state=random_state).fit(Xb)
            Wkb = _disp(Xb, kmb.labels_, kmb.cluster_centers_)
            ref_logs.append(np.log(Wkb))

        gap_k = np.mean(ref_logs) - logWk
        if gap_k > best_gap:
            best_gap, best_k = gap_k, k

    # 4) fit final and identify red cluster
    km = KMeans(n_clusters=best_k, random_state=random_state)
    labels = km.fit_predict(X_scaled)
    ctrs = km.cluster_centers_
    # undo scaling to compute composites
    ctr_raw = scaler.inverse_transform(ctrs)
    # composite = avg_z^9 + max_z^5 + proportion*100
    composites = ctr_raw[:, 0] + ctr_raw[:, 1] + ctr_raw[:, 3]
    red_lbl = int(np.argmax(composites))
    counts = np.bincount(labels, minlength=best_k)
    red_size = int(counts[red_lbl])

    # 4a) clear old flagged pairs
    FlaggedStudentPair.objects.filter(
        course_catalog_id=course_id,
        semester_id=semester_id,
    ).delete()

    # 4b) if red cluster small enough, flag them
    if red_size <= red_threshold:
        flagged_objs = []
        for ps, lbl in zip(pairs, labels):
            if lbl == red_lbl:
                # fallback if ps.max_similarity doesn't exist
                max_sim = getattr(ps, "max_similarity", ps.mean_similarity)
                flagged_objs.append(
                    FlaggedStudentPair(
                        course_catalog_id=course_id,
                        semester_id=semester_id,
                        student_a_id=ps.student_a_id,
                        student_b_id=ps.student_b_id,
                        mean_similarity=ps.mean_similarity,
                        max_similarity=max_sim,
                        mean_z_score=ps.mean_z_score,
                        max_z_score=ps.max_z_score,
                    )
                )

        if flagged_objs:
            with transaction.atomic():
                FlaggedStudentPair.objects.bulk_create(
                    flagged_objs, ignore_conflicts=True
                )

    # 5) remap PairFlagStat.kmeans_label so 0=lowest composite
    order = np.argsort(composites)
    remap = {old: new for new, old in enumerate(order)}
    for ps, lbl in zip(pairs, labels):
        ps.kmeans_label = remap[int(lbl)]

    with transaction.atomic():
        PairFlagStat.objects.bulk_update(pairs, ["kmeans_label"])

    print(
        f"✔️ run_kmeans_for_pair_stats done in {time.time() - start_ts:.2f}s; "
        f"red_size={red_size}"
    )
    return km


@require_GET
def kmeans_pairs_plot(request, course_id, semester_id):
    # 1) fetch all the pairs
    pairs = list(
        PairFlagStat.objects.filter(
            course_catalog_id=course_id,
            semester_id=semester_id,
        ).select_related("student_a", "student_b")
    )
    if not pairs:
        raise Http404()

    # 1a) student → cluster_label map
    profs = StudentSemesterProfile.objects.filter(
        course_catalog_id=course_id,
        semester_id=semester_id,
    ).only("student_id", "cluster_label")
    student_lbl = {p.student_id: (p.cluster_label or 0) for p in profs}

    # 2) build 5-dim feature matrix
    X_raw = np.vstack(
        [
            [
                ps.mean_z_score**9,
                ps.max_z_score**5,
                ps.mean_similarity**2,
                ps.proportion * 100.0,
                student_lbl.get(ps.student_a_id, 0)
                + student_lbl.get(ps.student_b_id, 0),
            ]
            for ps in pairs
        ]
    )
    labels = np.array([ps.kmeans_label for ps in pairs])

    # 3) Standardize + PCA → 2D
    X_scaled = StandardScaler().fit_transform(X_raw)
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X_scaled)
    dim1, dim2 = coords[:, 0], coords[:, 1]
    var1, var2 = pca.explained_variance_ratio_[:2] * 100

    # 4) find the “red” cluster by PC1 centroid
    unique_lbls = sorted(set(labels))
    centroids = {lbl: dim1[labels == lbl].mean() for lbl in unique_lbls}
    red_lbl = max(centroids, key=centroids.get)
    red_mask = labels == red_lbl
    red_n = int(red_mask.sum())

    # 5) decide rendering mode
    red_threshold = 30
    if red_n > red_threshold:
        # too many “reds”: highlight only the single worst point
        comps = X_raw[:, 0] + X_raw[:, 1] + X_raw[:, 3]
        worst_idx = int(np.argmax(comps))
        highlight = np.zeros_like(labels, dtype=bool)
        highlight[worst_idx] = True

        low_mask, med_mask, high_mask = (
            ~highlight,
            np.zeros_like(labels, bool),
            highlight,
        )
        low_n, med_n, high_n = int(low_mask.sum()), 0, 1
        highlight_color = "gold"
        highlight_label = "Outlier Candidate (n=1)"
        show_names = False
    else:
        # normal low/med/high split
        low_lbl = min(centroids, key=centroids.get)
        med_lbls = [l for l in unique_lbls if l not in (low_lbl, red_lbl)]

        low_mask = labels == low_lbl
        med_mask = np.isin(labels, med_lbls)
        high_mask = red_mask
        low_n, med_n, high_n = int(low_mask.sum()), int(med_mask.sum()), red_n

        highlight_color = "darkred"
        highlight_label = f"High Intensity (n={high_n})"
        show_names = True

    # 6) plotting
    fig = plt.figure(figsize=(14, 9))
    ax = fig.add_axes([0.00, 0.04, 0.78, 0.96])

    def plot_group(mask, color, marker, label):
        xi, yi = dim1[mask], dim2[mask]
        ax.scatter(
            xi, yi, c=color, marker=marker, s=100, edgecolor="k", alpha=0.8, label=label
        )
        pts = list(zip(xi, yi))
        if len(pts) >= 3:
            try:
                hull = ConvexHull(pts)
                hx, hy = zip(*(pts[i] for i in hull.vertices))
                ax.fill(hx, hy, color=color, alpha=0.2)
            except QhullError:
                pass
        elif pts:
            cx, cy = xi.mean(), yi.mean()
            r = (np.hypot(xi - cx, yi - cy).max() if len(xi) > 1 else 0.5) * 1.5
            ax.add_patch(Circle((cx, cy), radius=r, color=color, alpha=0.2))

    # plot low (always green)
    plot_group(low_mask, "green", "o", f"Low Intensity (n={low_n})")
    # plot medium if present
    if med_n:
        plot_group(med_mask, "gold", "s", f"Medium Intensity (n={med_n})")
    # plot high or highlight
    plot_group(high_mask, highlight_color, "^", highlight_label)

    # annotate & sidebar for true high cluster only
    if show_names and high_n:
        idxs = np.where(high_mask)[0]
        for num, i in enumerate(idxs, start=1):
            ax.annotate(
                str(num),
                xy=(dim1[i], dim2[i]),
                xytext=(4, 4),
                textcoords="offset points",
                fontsize=11,
                fontweight="bold",
                color=highlight_color,
            )
        # sidebar names
        names = [
            f"{pairs[i].student_a.first_name} {pairs[i].student_a.last_name} & "
            f"{pairs[i].student_b.first_name} {pairs[i].student_b.last_name}"
            for i in idxs
        ]
        y0, y1 = 0.98, 0.04
        dy = (y0 - y1) / (len(names) + 1)
        for j, txt in enumerate(names, start=1):
            fig.text(
                0.79,
                y0 - j * dy,
                f"{j}: {txt} (max_z={pairs[idxs[j-1]].max_z_score:.2f})",
                transform=fig.transFigure,
                va="top",
                ha="left",
                fontsize=11,
                fontweight="bold",
                color=highlight_color,
                family="monospace",
            )
    elif not show_names:
        # display a short message instead of sidebar
        fig.text(
            0.79,
            0.5,
            "Not enough evidence of anomalies",
            transform=fig.transFigure,
            va="center",
            ha="left",
            fontsize=14,
            fontstyle="italic",
        )

    # 7) axes, titles, legend
    ax.set_xlabel(f"Dimension 1 ({var1:.1f}% var)", fontsize=12)
    ax.set_ylabel(f"Dimension 2 ({var2:.1f}% var)", fontsize=12)

    course = get_object_or_404(CourseCatalog, pk=course_id)
    semester = get_object_or_404(Semester, pk=semester_id)
    ax.set_title(f"K-Means Clusters → {course} Pairs → {semester}", fontsize=16, pad=15)
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.7)

    fig.subplots_adjust(bottom=0.06)
    # legend: only two columns if no medium/high names
    ncols = 2 if (med_n == 0) else 3
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.50, -0.18),
        ncol=ncols,
        title="Pair Groups",
        frameon=True,
        fontsize=11,
        title_fontsize=13,
    )

    # 8) render PNG
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return HttpResponse(buf.read(), content_type="image/png")


def _generate_one(assignment_id):
    """
    Helper for ThreadPoolExecutor: close the old DB connection
    then run the report service in a fresh one.
    """
    connection.close()
    return generate_report_service(assignment_id)


@require_GET
def run_full_pipeline(request, course_id, semester_id):
    """
    0) Clear ALL AssignmentReport rows for this course+semester
    1) Clear PairFlagStat once
    2) Parallel–generate each assignment report (+ collect flagged pairs)
    3) Bulk–upsert all PairFlagStat in one go
    4) Clear & recompute StudentSemesterProfile
    5) Run student K-Means (capture model)
    6) Run pair K-Means (inject student labels)
    """
    start_ts = time.time()
    print(
        f"\n🚀 [PIPELINE] Starting full pipeline "
        f"for course={course_id}, semester={semester_id}"
    )

    # 0) DELETE all old AssignmentReport rows (and cascade StudentReports)
    AssignmentReport.objects.filter(
        assignment__course_catalog_id=course_id,
        assignment__semester_id=semester_id,
    ).delete()
    print("  🔄 Cleared old AssignmentReport rows")

    # 1) DELETE all old PairFlagStat rows
    PairFlagStat.objects.filter(
        course_catalog_id=course_id,
        semester_id=semester_id,
    ).delete()
    print("  🔄 Cleared old PairFlagStat rows")

    # 2) FETCH assignments
    assignments = list(
        Assignments.objects.filter(
            course_catalog_id=course_id,
            semester_id=semester_id,
        )
    )
    if not assignments:
        raise Http404("No assignments for that course+semester.")
    print(f"  📋 Found {len(assignments)} assignments; generating in parallel…")

    # 2a) generate each report in parallel, collect flagged pairs
    all_flagged = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(_generate_one, a.id): a for a in assignments}
        for fut in as_completed(futures):
            a = futures[fut]
            try:
                report, flagged = fut.result()
            except Exception as e:
                print(f"  ❌ generate_report({a.id}) failed:", e)
                continue
            if report:
                print(f"    ▶ report.id={report.id}, flagged_pairs={len(flagged)}")
                all_flagged.extend(flagged)

    # 3) BULK-UPSERT all flagged pairs once
    print(f"  🔄 Bulk-upserting {len(all_flagged)} flagged entries…")
    inserted = update_all_pair_stats(course_id, semester_id, all_flagged)
    print(f"    ✔️ update_all_pair_stats inserted/updated {inserted} rows")

    # 4) CLEAR & recompute StudentSemesterProfile
    StudentSemesterProfile.objects.filter(
        course_catalog_id=course_id,
        semester_id=semester_id,
    ).delete()
    print("  🔄 Cleared old StudentSemesterProfile rows")
    print("  🔄 Recomputing StudentSemesterProfile features")
    t0 = time.time()
    bulk_recompute_semester_profiles(course_id, semester_id)
    print(f"  ✔️ Profiles recomputed in {time.time() - t0:.2f}s")

    # 5) RUN student K-Means & keep the model
    print("  🔄 Running student KMeans")
    t1 = time.time()
    student_km = run_kmeans_for_course_semester(course_id, semester_id)
    print(
        f"  ✔️ Student KMeans done in {time.time() - t1:.2f}s "
        f"(k={student_km.n_clusters})"
    )

    # 6) RUN pair K-Means (inject student_km)
    print("  🔄 Running pair KMeans")
    t2 = time.time()
    run_kmeans_for_pair_stats(
        course_id=course_id,
        semester_id=semester_id,
        student_km=student_km,
        n_clusters=6,
        random_state=0,
        b_refs=10,
    )
    print(f"  ✔️ Pair KMeans done in {time.time() - t2:.2f}s")

    total = time.time() - start_ts
    print(f"✅ [PIPELINE] Finished full pipeline in {total:.2f}s\n")
    return JsonResponse({"status": "success", "duration_s": total})
