# backend/cheating/management/commands/populate_cs472_dummy.py

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
    help = "Populate dummy data for CS472 (3 sections) with 6 cheaters per section; symmetric similarity scores"

    def handle(self, *args, **options):
        with transaction.atomic():
            # SubmissionSimilarityPairs.objects.all().delete()

            semester, _ = Semester.objects.get_or_create(
                year=2025,
                term="Spring",
                session="Regular",
                defaults={"name": "Spring 2025 – Regular"},
            )

            User = get_user_model()
            base_nshe = 800_000
            base_codegd = 900_000

            def create_prof(section):
                username = f"prof_cs472_{section}"
                email = f"{username}@example.edu"
                user, _ = User.objects.get_or_create(
                    username=username,
                    defaults={"email": email, "password": "pbkdf2_sha256$dummy"},
                )
                return Professors.objects.get_or_create(user=user)[0]

            def get_course():
                course, _ = CourseCatalog.objects.get_or_create(
                    subject="CS",
                    catalog_number=472,
                    defaults={
                        "name": "CS472",
                        "course_title": "Capstone Project",
                        "course_level": "400",
                    },
                )
                return course

            def create_students(start_index, count, prefix):
                students = []
                for i in range(count):
                    idx = start_index + i
                    ace = f"{prefix.upper()}{idx:03}"
                    email = f"{prefix.lower()}{idx}@example.edu"
                    s, _ = Students.objects.get_or_create(
                        ace_id=ace,
                        defaults={
                            "email": email,
                            "nshe_id": base_nshe + idx,
                            "codegrade_id": base_codegd + idx,
                            "first_name": "Student",
                            "last_name": str(idx),
                        },
                    )
                    students.append(s)
                return students

            def create_assignments(course, sem):
                assigns = []
                start_due = date(2025, 2, 1)
                for num in range(1, 11):
                    due = start_due + timedelta(weeks=(num - 1))
                    lock = due + timedelta(hours=2)
                    a, _ = Assignments.objects.get_or_create(
                        course_catalog=course,
                        semester=sem,
                        assignment_number=num,
                        defaults={
                            "title": f"Assignment {num}",
                            "due_date": due,
                            "lock_date": lock,
                            "has_base_code": False,
                            "moss_report_directory_path": f"/tmp/moss/CS472_{num}",
                            "bulk_ai_directory_path": f"/tmp/ai/CS472_{num}",
                            "language": "python",
                            "has_policy": False,
                            "pdf_filepath": f"/tmp/pdfs/CS472_{num}.pdf",
                        },
                    )
                    assigns.append(a)
                return assigns

            def add_submissions(assignments, students, inst):
                submap = {}
                for a in assignments:
                    for s in students:
                        sub, _ = Submissions.objects.get_or_create(
                            assignment=a,
                            student=s,
                            course_instance=inst,
                            defaults={
                                "grade": round(random.uniform(60, 100), 2),
                                "created_at": a.due_date - timedelta(days=1),
                                "flagged": False,
                                "file_path": f"/submissions/{s.ace_id}/a{a.assignment_number}.py",
                            },
                        )
                        submap[(a.pk, s.pk)] = sub
                return submap

            def seed_symmetric_pairs(assignments, students, submap, num_cheaters):
                cheaters = random.sample(students, num_cheaters)
                for c in cheaters:
                    c.first_name = "Cheater"
                    c.save(update_fields=["first_name"])

                cheat_assignments = set(random.sample(assignments, 4))

                for a in assignments:
                    seen = set()
                    for i, s1 in enumerate(students):
                        for j in range(i + 1, len(students)):
                            s2 = students[j]
                            sub1 = submap[(a.pk, s1.pk)]
                            sub2 = submap[(a.pk, s2.pk)]

                            if sub1.pk > sub2.pk:
                                sub1, sub2 = sub2, sub1

                            pair_key = (sub1.pk, sub2.pk)
                            if pair_key in seen:
                                continue
                            seen.add(pair_key)

                            if (
                                a in cheat_assignments
                                and s1 in cheaters
                                and s2 in cheaters
                            ):
                                sim = random.randint(40, 55)
                                fname = "__all__"
                            else:
                                sim = random.randint(5, 35)
                                fname = "sample.py"

                            SubmissionSimilarityPairs.objects.get_or_create(
                                assignment=a,
                                submission_id_1=sub1,
                                submission_id_2=sub2,
                                defaults={
                                    "file_name": fname,
                                    "match_id": random.randint(10000, 99999),
                                    "percentage": sim,
                                },
                            )

            course = get_course()
            for section in (1, 2, 3):
                prof = create_prof(section)
                inst, _ = CourseInstances.objects.get_or_create(
                    course_catalog=course,
                    semester=semester,
                    section_number=section,
                    defaults={
                        "professor": prof,
                        "canvas_course_id": 7000 + section,
                    },
                )
                students = create_students(section * 100, 35, prefix="CS472")
                assignments = create_assignments(course, semester)
                submap = add_submissions(assignments, students, inst)
                seed_symmetric_pairs(assignments, students, submap, num_cheaters=6)

            self.stdout.write(
                self.style.SUCCESS(
                    "✅ Dummy CS472 data loaded with 3 sections — Cheaters: 40–55%, Non-Cheaters: 5–35%, Symmetric!"
                )
            )
