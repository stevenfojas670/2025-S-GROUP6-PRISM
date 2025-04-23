# backend/cheating/management/commands/populate_cs481_dummy.py

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
    help = "Populate dummy data for CS481 with 5 sections, 4 cheaters total, symmetric similarities"

    def handle(self, *args, **options):
        with transaction.atomic():
            # clear old similarity data
            # SubmissionSimilarityPairs.objects.all().delete()

            # make sure semester exists
            semester, _ = Semester.objects.get_or_create(
                year=2025,
                term="Spring",
                session="Regular",
                defaults={"name": "Spring 2025 – Regular"},
            )

            User = get_user_model()
            base_nshe = 700_000
            base_codegd = 800_000

            def create_prof(section):
                uname = f"prof_cs481_{section}"
                email = f"{uname}@example.edu"
                user, _ = User.objects.get_or_create(
                    username=uname,
                    defaults={"email": email, "password": "pbkdf2_sha256$dummy"},
                )
                return Professors.objects.get_or_create(user=user)[0]

            def get_course():
                course, _ = CourseCatalog.objects.get_or_create(
                    subject="CS",
                    catalog_number=481,
                    defaults={
                        "name": "CS481",
                        "course_title": "Capstone in Cybersecurity",
                        "course_level": "400",
                    },
                )
                return course

            def create_students(start_index, count):
                students = []
                for i in range(count):
                    idx = start_index + i
                    ace = f"CS481{idx:03}"
                    email = f"cs481_{idx}@example.edu"
                    student, _ = Students.objects.get_or_create(
                        ace_id=ace,
                        defaults={
                            "email": email,
                            "nshe_id": base_nshe + idx,
                            "codegrade_id": base_codegd + idx,
                            "first_name": "Student",
                            "last_name": str(idx),
                        },
                    )
                    students.append(student)
                return students

            def create_assignments(course, semester):
                assignments = []
                start_due = date(2025, 1, 20)
                for i in range(1, 9):  # 8 assignments
                    due = start_due + timedelta(weeks=i - 1)
                    lock = due + timedelta(hours=2)
                    a, _ = Assignments.objects.get_or_create(
                        course_catalog=course,
                        semester=semester,
                        assignment_number=i,
                        defaults={
                            "title": f"Assignment {i}",
                            "due_date": due,
                            "lock_date": lock,
                            "has_base_code": False,
                            "language": "python",
                            "pdf_filepath": f"/tmp/pdfs/CS481_{i}.pdf",
                            "moss_report_directory_path": f"/tmp/moss/CS481_{i}",
                            "bulk_ai_directory_path": f"/tmp/ai/CS481_{i}",
                            "has_policy": False,
                        },
                    )
                    assignments.append(a)
                return assignments

            def add_submissions(assignments, students, instance):
                submap = {}
                for a in assignments:
                    for s in students:
                        sub, _ = Submissions.objects.get_or_create(
                            assignment=a,
                            student=s,
                            course_instance=instance,
                            defaults={
                                "grade": round(random.uniform(60, 100), 2),
                                "created_at": a.due_date - timedelta(days=1),
                                "flagged": False,
                                "file_path": f"/submissions/{s.ace_id}/a{a.assignment_number}.py",
                            },
                        )
                        submap[(a.pk, s.pk)] = sub
                return submap

            def create_symmetrical_pairs(assignments, students, submap, cheaters):
                cheat_assigns = set(random.sample(assignments, 2))

                for a in assignments:
                    # Cheaters get high similarity scores on 2 assignments
                    if a in cheat_assigns:
                        for i in range(len(cheaters)):
                            for j in range(i + 1, len(cheaters)):
                                s1 = submap[(a.pk, cheaters[i].pk)]
                                s2 = submap[(a.pk, cheaters[j].pk)]
                                if s1.pk > s2.pk:
                                    s1, s2 = s2, s1
                                SubmissionSimilarityPairs.objects.get_or_create(
                                    assignment=a,
                                    submission_id_1=s1,
                                    submission_id_2=s2,
                                    defaults={
                                        "file_name": "__all__",
                                        "match_id": random.randint(10_000, 99_999),
                                        "percentage": random.randint(40, 55),
                                    },
                                )

                    # All other students (including cheaters on other assignments) get 5–35% similarities
                    for i in range(len(students)):
                        for j in range(i + 1, len(students)):
                            sA, sB = students[i], students[j]
                            if a in cheat_assigns and sA in cheaters and sB in cheaters:
                                continue  # skip already created cheater pairs
                            sub1 = submap[(a.pk, sA.pk)]
                            sub2 = submap[(a.pk, sB.pk)]
                            if sub1.pk > sub2.pk:
                                sub1, sub2 = sub2, sub1
                            SubmissionSimilarityPairs.objects.get_or_create(
                                assignment=a,
                                submission_id_1=sub1,
                                submission_id_2=sub2,
                                defaults={
                                    "file_name": "sample.py",
                                    "match_id": random.randint(20_000, 29_999),
                                    "percentage": random.randint(5, 35),
                                },
                            )

            # ────────────────────── START EXECUTION ──────────────────────
            course = get_course()
            section_count = 5
            total_cheaters_needed = 4
            cheaters_so_far = 0
            global_index = 0

            for sec in range(1, section_count + 1):
                prof = create_prof(sec)
                instance, _ = CourseInstances.objects.get_or_create(
                    course_catalog=course,
                    semester=semester,
                    section_number=sec,
                    defaults={"professor": prof, "canvas_course_id": 9000 + sec},
                )

                students = create_students(global_index * 100, 30)
                global_index += 1
                assignments = create_assignments(course, semester)
                submap = add_submissions(assignments, students, instance)

                # Only pick cheaters from current section if needed
                local_cheaters = []
                if cheaters_so_far < total_cheaters_needed:
                    remaining = total_cheaters_needed - cheaters_so_far
                    local_cheaters = random.sample(students, remaining)
                    for c in local_cheaters:
                        c.first_name = "Cheater"
                        c.save(update_fields=["first_name"])
                    cheaters_so_far += len(local_cheaters)

                create_symmetrical_pairs(assignments, students, submap, local_cheaters)

            self.stdout.write(
                self.style.SUCCESS(
                    "✅ Dummy CS481 data created for 5 sections — 4 cheaters total, symmetric sim scores"
                )
            )
