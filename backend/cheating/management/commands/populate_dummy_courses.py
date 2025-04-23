"""
Populate dummy data for multiple CS courses in Spring 2025 – Regular.

This command handles CS202, CS135, CS302, CS326, CS372, and CS218.
For each course it:
  1. Ensures the semester exists.
  2. Clears old submissions & similarity pairs.
  3. Creates sections with professors and students.
  4. Randomly selects 4–8 cheaters total per course.
  5. Generates assignments and one submission per student.
  6. Seeds symmetric similarity pairs with higher values for cheaters.
"""

import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

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
    """Django management command to bulk-populate dummy courses."""

    help = (
        "Populate dummy data for CS202, CS135, CS302, CS326, CS372, CS218 "
        "— each with 4–8 cheaters total."
    )

    def handle(self, *args, **options):
        """
        Entry point for populate_dummy_courses.

        Wrap everything in a single transaction to ensure atomicity.
        """
        with transaction.atomic():
            # 1) Ensure our semester exists
            semester, _ = Semester.objects.get_or_create(
                year=2025,
                term="Spring",
                session="Regular",
                defaults={"name": "Spring 2025 – Regular"},
            )
            User = get_user_model()

            # 2) Define each course’s config
            configs = [
                # existing courses
                {
                    "subject": "CS",
                    "catalog": 202,
                    "sections": random.randint(3, 5),
                    "students_fn": lambda: random.randint(30, 40),
                    "assigns": random.randint(7, 10),
                    "cheaters": random.randint(4, 8),
                },
                {
                    "subject": "CS",
                    "catalog": 135,
                    "sections": 3,
                    "students_fn": lambda: 40,
                    "assigns": 8,
                    "cheaters": random.randint(4, 8),
                },
                {
                    "subject": "CS",
                    "catalog": 302,
                    "sections": random.randint(3, 5),
                    "students_fn": lambda: random.randint(30, 40),
                    "assigns": random.randint(7, 10),
                    "cheaters": random.randint(4, 8),
                },
                # newly requested courses
                {
                    "subject": "CS",
                    "catalog": 326,
                    "sections": random.randint(3, 5),
                    "students_fn": lambda: random.randint(30, 40),
                    "assigns": random.randint(8, 10),
                    "cheaters": random.randint(4, 8),
                },
                {
                    "subject": "CS",
                    "catalog": 372,
                    "sections": random.randint(3, 5),
                    "students_fn": lambda: random.randint(30, 40),
                    "assigns": random.randint(8, 10),
                    "cheaters": random.randint(4, 8),
                },
                {
                    "subject": "CS",
                    "catalog": 218,
                    "sections": random.randint(3, 5),
                    "students_fn": lambda: random.randint(30, 40),
                    "assigns": random.randint(8, 10),
                    "cheaters": random.randint(4, 8),
                },
            ]

            # 3) Loop through each config and populate
            for cfg in configs:
                subj, cat = cfg["subject"], cfg["catalog"]
                self.stdout.write(f"\n📦 Populating {subj}{cat}…")
                self._populate_course(
                    semester=semester,
                    subject=subj,
                    catalog=cat,
                    num_sections=cfg["sections"],
                    students_per_section_fn=cfg["students_fn"],
                    num_assigns=cfg["assigns"],
                    total_cheaters=cfg["cheaters"],
                )

            self.stdout.write(
                self.style.SUCCESS("\n✅ All dummy courses complete!")
            )

    # ─────────────────── Helper methods ───────────────────

    def _get_or_create_course(self, subject, catalog):
        """
        Fetch or create the CourseCatalog entry for a subject and catalog.
        """
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
        """
        Create a dummy Professor + User for a given section.
        """
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
        Create `count` Students starting at index `start_idx`.
        """
        students = []
        for i in range(count):
            idx = start_idx + i
            ace = f"X{idx:05}"
            student, _ = Students.objects.get_or_create(
                ace_id=ace,
                defaults={
                    "email": f"{ace}@example.edu",
                    "nshe_id": 900000 + idx,
                    "codegrade_id": 1000000 + idx,
                    "first_name": "Student",
                    "last_name": str(idx),
                },
            )
            students.append(student)
        return students

    def _create_assignments(self, course, semester, count):
        """
        Create `count` weekly Assignments starting Jan 15 2025.
        """
        assignments = []
        due_start = date(2025, 1, 15)
        for num in range(1, count + 1):
            due = due_start + timedelta(weeks=num - 1)
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
                        f"/tmp/pdfs/{course.subject}"
                        f"{course.catalog_number}_{num}.pdf"
                    ),
                    "moss_report_directory_path": (
                        f"/tmp/moss/{course.subject}"
                        f"{course.catalog_number}_{num}"
                    ),
                    "bulk_ai_directory_path": (
                        f"/tmp/ai/{course.subject}"
                        f"{course.catalog_number}_{num}"
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
        Core logic to populate one course:
          A) Clear old data
          B) Create sections + students
          C) Select & rename cheaters
          D) Generate assignments
          E) Bulk-create Submissions
          F) Build lookup map
          G) Bulk-create symmetric similarity pairs
          H) Print summary
        """
        course = self._get_or_create_course(subject, catalog)

        # A) Clear out any existing submissions & similarity pairs
        SubmissionSimilarityPairs.objects.filter(
            assignment__course_catalog=course,
            assignment__semester=semester,
        ).delete()
        Submissions.objects.filter(
            assignment__course_catalog=course,
            assignment__semester=semester,
        ).delete()
        self.stdout.write("  🔄 Cleared old data")

        # B) Spin up sections, professors, and student groups
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

        all_students = [s for _, group in section_groups for s in group]

        # C) Pick total_cheaters randomly, rename them “Cheater”
        cheaters = random.sample(all_students, total_cheaters)
        for student in cheaters:
            student.first_name = "Cheater"
            student.save(update_fields=["first_name"])

        # D) Create the specified assignments for this course
        assignments = self._create_assignments(course, semester, num_assigns)

        # E) Bulk-create one submission per student per assignment
        subs_to_create = []
        for inst, group in section_groups:
            for a in assignments:
                for s in group:
                    path = (
                        f"/submissions/{subject}{catalog}"
                        f"/sec{inst.section_number}/{s.ace_id}"
                        f"/a{a.assignment_number}.py"
                    )
                    subs_to_create.append(
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
        Submissions.objects.bulk_create(
            subs_to_create, ignore_conflicts=True
        )
        self.stdout.write(
            f"  ✔️ Created {len(subs_to_create)} submissions"
        )

        # F) Build a lookup for assignment+student → submission
        subs = Submissions.objects.filter(
            assignment__course_catalog=course,
            assignment__semester=semester,
        ).only("id", "assignment_id", "student_id")
        submap = {
            (sub.assignment_id, sub.student_id): sub for sub in subs
        }

        # G) Bulk-create symmetric similarity pairs
        pairs_to_create = []
        for a in assignments:
            # Choose 2–4 assignments where cheaters pair with high similarity
            cheat_on = set(
                random.sample(assignments, random.randint(2, 4))
            )

            # 1) Cheater↔Cheater with 40–60% similarity
            if a in cheat_on:
                for i in range(len(cheaters)):
                    for j in range(i + 1, len(cheaters)):
                        s1 = submap[(a.pk, cheaters[i].pk)]
                        s2 = submap[(a.pk, cheaters[j].pk)]
                        if s1.pk > s2.pk:
                            s1, s2 = s2, s1
                        pairs_to_create.append(
                            SubmissionSimilarityPairs(
                                assignment_id=a.pk,
                                submission_id_1_id=s1.pk,
                                submission_id_2_id=s2.pk,
                                file_name="__all__",
                                match_id=random.randint(10000, 99999),
                                percentage=random.randint(40, 60),
                            )
                        )

            # 2) All other pairs with 5–35% similarity
            for i in range(len(all_students)):
                for j in range(i + 1, len(all_students)):
                    si, sj = all_students[i], all_students[j]
                    if (
                        a in cheat_on
                        and si in cheaters
                        and sj in cheaters
                    ):
                        continue  # skip already added
                    s1 = submap[(a.pk, si.pk)]
                    s2 = submap[(a.pk, sj.pk)]
                    if s1.pk > s2.pk:
                        s1, s2 = s2, s1
                    pairs_to_create.append(
                        SubmissionSimilarityPairs(
                            assignment_id=a.pk,
                            submission_id_1_id=s1.pk,
                            submission_id_2_id=s2.pk,
                            file_name="sample.py",
                            match_id=random.randint(20000, 29999),
                            percentage=random.randint(5, 35),
                        )
                    )

        SubmissionSimilarityPairs.objects.bulk_create(
            pairs_to_create, ignore_conflicts=True
        )
        self.stdout.write(
            f"  ✔️ Created {len(pairs_to_create)} similarity pairs"
        )

        # H) Final summary for this course
        self.stdout.write(
            self.style.SUCCESS(
                f"  → {subject}{catalog}: "
                f"{num_sections} sections, "
                f"{len(all_students)} students, "
                f"{num_assigns} assignments, "
                f"{total_cheaters} cheaters total"
            )
        )