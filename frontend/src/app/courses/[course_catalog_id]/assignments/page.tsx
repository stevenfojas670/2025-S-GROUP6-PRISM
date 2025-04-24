"use client"
import React, { useEffect, useState } from "react"
import {
	Typography,
	ButtonBase,
	Box,
	Button,
	List,
	ListItemButton,
	ListItemText,
} from "@mui/material"
import { useRouter } from "next/navigation"
import { easyFetch } from "@/utils/fetchWrapper"
import { useParams } from "next/navigation"
import { useCourseContext } from "@/context/CourseContext"
import { GetStudents } from "@/controllers/students"
import { StudentEnrollments } from "@/types/studentTypes"
import { blueGrey, grey } from "@mui/material/colors"
import { GetSimilarityPlot } from "@/controllers/graphs"
/**
 * This will be used for pagination if necessary
 */
interface AssignmentResponse {
	count: number
	next: null
	previous: null
}

interface AssignmentItem {
	id: number
	assignment_number: number
	title: string
	lock_date: string | null
	pdf_filepath: string | null
	has_base_code: boolean | null
	moss_report_directory_path: string | null
	bulk_ai_directory_path: string | null
	language: string | null
	has_policy: boolean | null
	course_instance: number
}

export default function Assignments() {
	const router = useRouter()
	const [assignments, setAssignments] = useState<AssignmentItem[]>([])
	const [assignmentImages, setAssignmentImages] = useState<
		Record<number, string>
	>({})
	const [students, setStudents] = useState<StudentEnrollments[]>([])
	const { courseInstanceId, semesterId } = useCourseContext()
	const { course_catalog_id } = useParams()

	useEffect(() => {
		if (!course_catalog_id) return
		const fetchAssignments = async () => {
			try {
				const queryParams = new URLSearchParams({
					course_catalog: String(course_catalog_id),
				})

				const response = await easyFetch(
					`http://localhost:8000/api/assignment/assignments?${queryParams}`,
					{
						method: "get",
					}
				)

				const data = await response.json()

				if (response.ok) {
					setAssignments(data.results)
				}
			} catch (error) {
				console.error(error)
			}
		}

		const fetchStudents = async () => {
			if (!courseInstanceId) return
			const data = await GetStudents(Number(courseInstanceId))
			if ("results" in data) {
				setStudents(data.results)
			} else {
				console.error("Error fetching students.", data)
			}
		}

		fetchAssignments()
		fetchStudents()
	}, [course_catalog_id, courseInstanceId])

	// Fetching plots for each assignment
	useEffect(() => {
		if (assignments.length === 0) return

		const fetchImages = async () => {
			const imageMap: Record<number, string> = {}

			for (const assignment of assignments) {
				const imgUrl = await GetSimilarityPlot(assignment.id)
				if (imgUrl) {
					imageMap[assignment.id] = imgUrl
				} else {
					imageMap[assignment.id] = "" // explicit empty string to indicate missing image
				}
			}

			setAssignmentImages(imageMap)
		}

		fetchImages()
	}, [assignments])

	return (
		<Box sx={{ display: "flex", gap: 2 }}>
			{/* Body Container */}
			<Box
				sx={(theme) => ({
					backgroundColor: theme.palette.background.paper,
					p: 2,
					boxShadow: 2,
					overflowX: "auto",
				})}
			>
				{/* Page buttons */}
				<Box
					sx={{
						display: "flex",
						gap: 2,
						mb: 2,
					}}
				>
					<Button variant="contained">Upload Assignment</Button>
					<Button variant="contained">Export All</Button>
				</Box>
				{/* Assignments Container */}
				<Box
					sx={{
						display: "flex",
						flexWrap: "wrap",
						gap: 2,
					}}
				>
					{/* Assignments Cards */}
					{assignments.map((assignment) => (
						<Box
							key={assignment.id}
							sx={(theme) => ({
								minWidth: 450,
								height: assignmentImages[assignment.id] ? "auto" : "100px",
								display: "block",
								borderRadius: 2,
								px: 2,
								py: 2,
								boxShadow: 2,
								backgroundColor: blueGrey[100],
								position: "relative",
							})}
						>
							<Typography
								sx={{
									position: "absolute",
									top: 12,
									right: 15,
									":hover": {
										cursor: "pointer",
									},
								}}
							>
								<Button
									variant="contained"
									disabled={!assignmentImages[assignment.id]}
									onClick={() =>
										router.push(
											`/courses/${course_catalog_id}/assignments/graphs?assignment=${assignment.id}`
										)
									}
								>
									Details
								</Button>
							</Typography>
							<Box>
								<Typography>{assignment.title}</Typography>
							</Box>
							{/* Image Container */}
							<Box
								sx={{
									mt: 2,
									height: "420px",
									width: "100%",
									overflowX: "auto",
									overflowY: "hidden",
									borderRadius: "4px",
									position: "relative",
								}}
							>
								{assignmentImages[assignment.id] ? (
									<Box
										component="img"
										src={assignmentImages[assignment.id]}
										alt="Similarity Plot"
										sx={{
											height: "100%",
										}}
									/>
								) : (
									<Typography variant="caption" color="textSecondary">
										No plot available.
									</Typography>
								)}
							</Box>
						</Box>
					))}
				</Box>
			</Box>
			{/* Students List */}
			<Box
				sx={(theme) => ({
					p: 2,
					minWidth: 200,
					maxWidth: 400,
					flexShrink: 0,
					flexGrow: 0,
					backgroundColor: theme.palette.background.paper,
					boxShadow: 2,
					position: "sticky",
					top: 0,
					height: "100vh",
					overflowY: "auto",
					zIndex: 10,
				})}
			>
				<Typography>Students</Typography>
				<List component="div" disablePadding>
					{students.map((student) => (
						<React.Fragment key={student.id}>
							<ListItemButton sx={{ width: "100%" }}>
								<ListItemText
									primary={`${student.student.first_name} ${student.student.last_name}`}
									sx={{ width: "100%" }}
								/>
							</ListItemButton>
						</React.Fragment>
					))}
				</List>
			</Box>
		</Box>
	)
}
