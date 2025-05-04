"use client"
import { Typography, Box, Divider } from "@mui/material"
import CustomCards from "@/components/CustomCards"
import { useParams, useRouter } from "next/navigation"
import { GetCourses } from "@/controllers/courses"
import { Course } from "@/types/coursesTypes"
import { useAuth } from "@/context/AuthContext"
import { useEffect, useState } from "react"

export default function Courses() {
	const router = useRouter()
	const { user } = useAuth()
	const params = useParams()
	const semesterId = params.semesters
	const [courses, setCourses] = useState<Course[]>([])
	const [loading, setLoading] = useState(true)

	useEffect(() => {
		if (!semesterId || !user) return
		const loadCourses = async () => {
			setLoading(true)
			const data = await GetCourses(Number(user?.pk), Number(semesterId))
			if ("results" in data) {
				setCourses(data.results)
			} else {
				console.error("Error fetching courses: ", data)
			}
			setLoading(false)
		}
		loadCourses()
	}, [user, semesterId])

	return (
		<Box
			sx={(theme) => ({
				backgroundColor: theme.palette.background.paper,
				height: "100%",
				p: 2,
			})}
		>
			<Box>
				<Typography variant="h4" gutterBottom>
					Courses
				</Typography>
				<Divider />
				<Box className="sections" sx={{ pt: 2 }}>
					{loading ? (
						<Typography>Loading courses...</Typography>
					) : (
						courses.map((course) => (
							<CustomCards
								key={course.id}
								onClick={() => router.push(`courses/${course.id}`)}
							>
								<Typography>{course.course_catalog.name}</Typography>
								<Typography>{course.section_number}</Typography>
							</CustomCards>
						))
					)}
				</Box>
			</Box>
		</Box>
	)
}
