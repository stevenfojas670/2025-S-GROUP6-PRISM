"use client"
import { Typography, Button, Box } from "@mui/material"
import CourseCards from "@/components/CourseCards"
import { useRouter } from "next/navigation"
import { GetCourses } from "@/controllers/courses"
import { Course, CourseCatalog, CourseResponse } from "@/types/coursesTypes"
import { useAuth } from "@/context/AuthContext"
import { useEffect, useState } from "react"
import { useSearchParams } from "next/navigation"
import { useCourseContext } from "@/context/CourseContext"

export default function Courses() {
	const router = useRouter()
	const { user } = useAuth()
	const { setCourseInstanceId, setSemesterId } = useCourseContext()
	const searchParams = useSearchParams()
	const semesterId = searchParams.get("semester")
	const [courses, setCourses] = useState<Course[]>([])

	const courseClick = (courseInstanceId: number, catalogId: number) => {
		setCourseInstanceId(courseInstanceId)
		setSemesterId(semesterId ? Number(semesterId) : null)
		router.push(`/courses/${catalogId}/assignments`)
	}

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
			<div>
				<div>
					<Typography>Welcome {user?.first_name}</Typography>
					<Typography>Professor ID: {user?.professor_id}</Typography>
					<Typography>User ID: {user?.pk}</Typography>
				</div>
				<div className="sections">
					{courses.map((course) => (
						<CourseCards
							key={course.id}
							onClick={() => courseClick(course.id, course.course_catalog.id)}
						>
							<Typography>{course.course_catalog.name}</Typography>
							<Typography>{course.section_number}</Typography>
						</CourseCards>
					))}
				</div>
			</div>
		</Box>
	)
}
