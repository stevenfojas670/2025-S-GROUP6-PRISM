"use client"
import { Typography, Button, Box } from "@mui/material"
import CourseCards from "@/components/CourseCards"
import { SignOutButton } from "@/components/AuthenticationMethod"
import { useRouter } from "next/navigation"
import { GetCourses } from "@/controllers/courses"
import { Course, CourseCatalog, CourseResponse } from "@/types/coursesTypes"
import { useAuth } from "@/context/AuthContext"
import { useEffect, useState } from "react"
import { useSearchParams } from "next/navigation"

export default function Courses() {
	const router = useRouter()
	const { user } = useAuth()
	const searchParams = useSearchParams()
	const semesterId = searchParams.get("semester")
	const [courses, setCourses] = useState<Course[]>([])

	useEffect(() => {
		if (!(semesterId && user?.professor_id)) return
		const loadCourses = async () => {
			const data = await GetCourses(
				Number(semesterId),
				Number(user?.professor_id)
			)
			if ("results" in data) {
				setCourses(data.results)
			} else {
				console.error("Error fetching courses: ", data)
			}
		}

		loadCourses()
	}, [semesterId])

	return (
		<Box>
			<SignOutButton />

			{/* Main banner */}
			<div>
				<div className="Banner">
					<Typography>Welcome {user?.first_name}</Typography>
					<h1>Professor ID: {user?.professor_id}</h1>
					<h1>User ID: {user?.pk}</h1>
				</div>

				{/* 2 buttons -> compare students, alerts */}
				<div className="comapreButtons">
					<button onClick={() => router.push("/student_comparison")}>
						Compare Students
					</button>
					<button onClick={() => router.push("/alerts")}>Alerts</button>
				</div>

				{/* Main Navigation */}
				<div className="sections">
					{courses.map((course) => (
						<CourseCards key={course.id}>
							<Typography>{course.course_catalog.name}</Typography>
						</CourseCards>
					))}
				</div>
			</div>
		</Box>
	)
}
