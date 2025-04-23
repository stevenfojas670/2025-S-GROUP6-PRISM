"""Populate dummy data for courses, students, and similarity pairs."""

import random
import os
from datetime import date, timedelta
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q

from courses.models import (
    CourseCatalog,
    Semester,
    CourseInstances,
    Students,
    Professors,
)
from assignments.models import Assignments, Submissions
from cheating.models import SubmissionSimilarityPairs


class Command(BaseCommand):
    """Django management command to bulk-populate dummy courses, students, and similarity data."""

    help = (
        "Populate dummy data for CS202, CS135, and CS302 "
        "using bulk_create for speed."
    )

    def handle(self, *args, **options):
        """Orchestrate creation of semesters, courses, sections, students, and similarity pairs."""
        with transaction.atomic():
            # 1) Ensure the Spring 2025 Regular semester exists
            semester, _ = Semester.objects.get_or_create(
                year=2025,
                term="Spring",
                session="Regular",
                defaults={"name": "Spring 2025 – Regular"},
            )
            User = get_user_model()

            # 2) Configuration for each dummy course
            configs = [
                {
                    "subject": "CS",
                    "catalog": 202,
                    "sections": random.randint(3, 5),
                    "students_fn": lambda: random.randint(30, 40),
                    "assignments": random.randint(7, 10),
                    "cheaters": random.randint(8, 14),
                },
                {
                    "subject": "CS",
                    "catalog": 135,
                    "sections": 3,
                    "students_fn": lambda: 40,
                    "assignments": 8,
                    "cheaters": 10,
                },
                {
                    "subject": "CS",
                    "catalog": 302,
                    "sections": random.randint(3, 5),
                    "students_fn": lambda: random.randint(30, 40),
                    "assignments": random.randint(7, 10),
                    "cheaters": random.randint(8, 14),
                },
            ]

            # Loop through config and build each course’s dummy data
            for cfg in configs:
                subj = cfg["subject"]
                cat = cfg["catalog"]
                self.stdout.write(f"\n📦 Populating {subj}{cat}…")
                self._populate_course(
                    semester=semester,
                    subject=subj,
                    catalog=cat,
                    num_sections=cfg["sections"],
                    students_per_section_fn=cfg["students_fn"],
                    num_assigns=cfg["assignments"],
                    total_cheaters=cfg["cheaters"],
                )

            self.stdout.write(self.style.SUCCESS(
                "✅ Dummy data populated for all courses!"
            ))

    # ──────────────────────── Helpers ────────────────────────

    def _get_or_create_course(self, subject, catalog):
        """Fetch or create a CourseCatalog entry for the given subject/catalog."""
        course, _ = CourseCatalog.objects.get_or_create(
            subject=subject,
            catalog_number=catalog,
            defaults={
                "name": f"{subject}{catalog}",
                "course_title": f"Dummy {subject}{catalog} Title",
                "course_level": str((catalog // 100) * 100),
            },
        )
        return course

    def _create_professor(self, section):
        """Make a dummy professor user for a given section (unique username)."""
        uname = f"prof_{section}_{random.randint(1000, 9999)}"
        user, _ = get_user_model().objects.get_or_create(
            username=uname,
            defaults={
                "email": f"{uname}@example.edu",
                "password": "pbkdf2_sha256$dummy",
            },
        )
        prof, _ = Professors.objects.get_or_create(user=user)
        return prof

    def _create_students(self, start_idx, count):
        """
        Create or fetch `count` Students starting at some index.

        We generate unique ACE/NSHE/CodeGrade IDs.
        """
        students = []
        for i in range(count):
            ace = f"X{start_idx + i:05}"
            s, _ = Students.objects.get_or_create(
                ace_id=ace,
                defaults={
                    "email": f"{ace}@example.edu",
                    "nshe_id": 900000 + start_idx + i,
                    "codegrade_id": 1000000 + start_idx + i,
                    "first_name": "Student",
                    "last_name": str(start_idx + i),
                },
            )
            students.append(s)
        return students

    def _create_assignments(self, course, semester, count):
        """
        Create `count` Assignments spaced one week apart starting Jan 15, 2025.

        Returns the list of created/fetched Assignments.
        """
        assignments = []
        start_due = date(2025, 1, 15)
        for num in range(1, count + 1):
            due = start_due + timedelta(weeks=num - 1)
            lock = due + timedelta(hours=2)
            a, _ = Assignments.objects.get_or_create(
                course_catalog=course,
                semester=semester,
                assignment_number=num,
                defaults={
                    "title": f"Assignment {num}",
                    "due_date": due,
                    "lock_date": lock,
                    "has_base_code": False,
                    "language": "python",
                    "pdf_filepath": (
                        f"/tmp/pdfs/{course.subject}{course.catalog_number}_"
                        f"{num}.pdf"
                    ),
                    "moss_report_directory_path": (
                        f"/tmp/moss/{course.subject}{course.catalog_number}_"
                        f"{num}"
                    ),
                    "bulk_ai_directory_path": (
                        f"/tmp/ai/{course.subject}{course.catalog_number}_{num}"
                    ),
                    "has_policy": False,
                },
            )
            assignments.append(a)
        return assignments

    def _populate_course(
        self,
        semester,
        subject,
        catalog,
        num_sections,
        students_per_section_fn,
        num_assigns,
        total_cheaters,
    ):
        """
        Core routine that:
          1) clears old data,
          2) creates sections with professors + students,
          3) marks random subset as “Cheater”,
          4) bulk-creates submissions,
          5) bulk-creates similarity pairs.
        """
        course = self._get_or_create_course(subject, catalog)

        # Purge prior submissions and similarity pairs for a clean slate
        SubmissionSimilarityPairs.objects.filter(
            assignment__course_catalog=course,
            assignment__semester=semester,
        ).delete()
        Submissions.objects.filter(
            assignment__course_catalog=course,
            assignment__semester=semester,
        ).delete()
        self.stdout.write(
            "  🔄 Cleared old submissions & similarity for this course"
        )

        # 1) Build one CourseInstance + its students for each section
        section_groups = []
        for sec in range(1, num_sections + 1):
            prof = self._create_professor(sec)
            inst, _ = CourseInstances.objects.get_or_create(
                course_catalog=course,
                semester=semester,
                section_number=sec,
                defaults={
                    "professor": prof,
                    "canvas_course_id": random.randint(20000, 29999),
                },
            )
            count = students_per_section_fn()
            studs = self._create_students((sec - 1) * 1000, count)
            section_groups.append((inst, studs))

        # Flatten to get the full student list
        all_students = [s for _, grp in section_groups for s in grp]

        # 2) Randomly tag a subset as cheaters (rename first_name)
        cheaters = random.sample(all_students, total_cheaters)
        for s in cheaters:
            s.first_name = "Cheater"
            s.save(update_fields=["first_name"])

        # 3) Set up assignments
        assignments = self._create_assignments(course, semester, num_assigns)

        # 4a) Build Submission objects in memory
        submission_objs = []
        for inst, group in section_groups:
            for a in assignments:
                for s in group:
                    path = (
                        f"/submissions/{subject}{catalog}/sec"
                        f"{inst.section_number}/{s.ace_id}/"
                        f"a{a.assignment_number}.py"
                    )
                    submission_objs.append(
                        Submissions(
                            assignment_id=a.pk,
                            student_id=s.pk,
                            course_instance_id=inst.pk,
                            grade=round(random.uniform(60, 100), 2),
                            created_at=a.due_date - timedelta(days=1),
                            flagged=False,
                            file_path=path,
                        )
                    )

        # 4b) Bulk-insert all submissions at once
        Submissions.objects.bulk_create(submission_objs, ignore_conflicts=True)
        self.stdout.write(
            f"  ✔️ Bulk‐created {len(submission_objs)} submissions"
        )

        # 4c) Re-fetch submissions to build a lookup map
        subs = Submissions.objects.filter(
            assignment__course_catalog=course,
            assignment__semester=semester,
        ).only("id", "assignment_id", "student_id")
        submap = {(sub.assignment_id, sub.student_id): sub for sub in subs}

        # 5a) Build all similarity-pair objects in memory
        pair_objs = []
        for a in assignments:
            # randomly choose which assignments have cheater↔cheater matches
            cheat_on = set(random.sample(assignments, random.randint(2, 5)))

            # create high-% pairs among cheaters on those flagged assignments
            if a in cheat_on:
                for i in range(len(cheaters)):
                    for j in range(i + 1, len(cheaters)):
                        s1 = submap[(a.pk, cheaters[i].pk)]
                        s2 = submap[(a.pk, cheaters[j].pk)]
                        if s1.pk > s2.pk:
                            s1, s2 = s2, s1
                        pair_objs.append(
                            SubmissionSimilarityPairs(
                                assignment_id=a.pk,
                                submission_id_1_id=s1.pk,
                                submission_id_2_id=s2.pk,
                                file_name="__all__",
                                match_id=random.randint(10000, 99999),
                                percentage=random.randint(40, 60),
                            )
                        )

            # then fill out the rest with normal ranges
            for i in range(len(all_students)):
                for j in range(i + 1, len(all_students)):
                    si, sj = all_students[i], all_students[j]
                    # skip cheater↔cheater combos if already done above
                    if (
                        a in cheat_on and
                        si in cheaters and
                        sj in cheaters
                    ):
                        continue

                    s1 = submap[(a.pk, si.pk)]
                    s2 = submap[(a.pk, sj.pk)]
                    if s1.pk > s2.pk:
                        s1, s2 = s2, s1

                    pair_objs.append(
                        SubmissionSimilarityPairs(
                            assignment_id=a.pk,
                            submission_id_1_id=s1.pk,
                            submission_id_2_id=s2.pk,
                            file_name="sample.py",
                            match_id=random.randint(20000, 29999),
                            percentage=random.randint(5, 35),
                        )
                    )

        # 5b) Bulk-insert all similarity pairs at once
        SubmissionSimilarityPairs.objects.bulk_create(
            pair_objs,
            ignore_conflicts=True,
        )
        self.stdout.write(
            f"  ✔️ Bulk‐created {len(pair_objs)} similarity pairs"
        )

        # Final summary status
        self.stdout.write(self.style.SUCCESS(
            f"  ✔️ {subject}{catalog}: "
            f"{num_sections} sections, "
            f"{len(all_students)} students, "
            f"{num_assigns} assignments, "
            f"{total_cheaters} cheaters"
        ))
