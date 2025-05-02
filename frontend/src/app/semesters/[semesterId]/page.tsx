"use client"
import { Typography, Box } from "@mui/material"
import CourseCards from "@/components/CourseCards"
import { useParams, useRouter } from "next/navigation"
import { GetCourses } from "@/controllers/courses"
import { Course } from "@/types/coursesTypes"
import { useAuth } from "@/context/AuthContext"
import { useEffect, useState } from "react"

export default function Courses() {
	const router = useRouter()
	const { user } = useAuth()
	const { semesterId } = useParams()
	const [courses, setCourses] = useState<Course[]>([])

	useEffect(() => {
		if (!semesterId || !user?.pk) return
		const loadCourses = async () => {
			const data = await GetCourses(Number(user?.pk), Number(semesterId))
			if ("results" in data) {
				setCourses(data.results)
			} else {
				console.error("Error fetching courses: ", data)
			}
		}

		loadCourses()
	}, [user?.pk, semesterId])

	return (
		<Box
			sx={(theme) => ({
				backgroundColor: theme.palette.background.paper,
				height: "100%",
				p: 2,
			})}
		>
			<Box>
				<Box sx={{ mb: 2 }}>
					<Typography variant="h4">Welcome {user?.first_name}</Typography>
				</Box>
				<Box className="sections">
					{courses.map((course) => (
						<CourseCards
							key={course.id}
							onClick={() => router.push(`courses/${course.id}`)}
						>
							<Typography>{course.course_catalog.name}</Typography>
							<Typography>{course.section_number}</Typography>
						</CourseCards>
					))}
				</Box>
			</Box>
		</Box>
	)
}
