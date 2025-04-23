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
import OpenInFullIcon from "@mui/icons-material/OpenInFull"
import { useCourseContext } from "@/context/CourseContext"
import { GetStudents } from "@/controllers/students"
import { StudentEnrollments } from "@/types/studentTypes"
import { blueGrey, grey } from "@mui/material/colors"
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
	const [assignments, setAssignments] = useState<AssignmentItem[]>([])
	const [students, setStudents] = useState<StudentEnrollments[]>([])
	const { courseInstanceId } = useCourseContext()
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

	return (
		<Box sx={{ display: "flex", gap: 2 }}>
			<Box
				sx={(theme) => ({
					backgroundColor: theme.palette.background.paper,
					p: 2,
					boxShadow: 2,
				})}
			>
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
				<Box sx={{ display: "flex" }}>
					<Box
						sx={{
							display: "flex",
							flexWrap: "wrap",
							gap: 2,
						}}
					>
						{assignments.map((assignment) => (
							<ButtonBase key={assignment.id}>
								<Box
									sx={(theme) => ({
										minWidth: 450,
										minHeight: 300,
										borderRadius: "10px",
										overflow: "hidden",
										display: "block",
										textAlign: "left",
										px: 2,
										py: 2,
										boxShadow: 2,
										backgroundColor: blueGrey[100],
										position: "relative",
										":hover": {
											cursor: "pointer",
										},
									})}
								>
									<OpenInFullIcon
										sx={{ position: "absolute", top: 8, right: 8 }}
									/>
									<Box>
										<Typography>{assignment.title}</Typography>
									</Box>
									<Box>Graph</Box>
								</Box>
							</ButtonBase>
						))}
					</Box>
				</Box>
			</Box>
			{/* Students List */}
			<Box
				sx={(theme) => ({
					p: 2,
					minWidth: 200, // make it wider
					maxWidth: 400,
					flexShrink: 0, // prevent shrinking
					flexGrow: 0, // prevent growing
					backgroundColor: theme.palette.background.paper,
					boxShadow: 2,
				})}
			>
				<Typography>Students</Typography>
				<List component="div" disablePadding>
					{students.map((student) => (
						<React.Fragment key={student.id}>
							<ListItemButton sx={{ width: "100%" }}>
								<ListItemText
									primary={`${student.student.first_name} ${student.student.last_name}`}
									sx={{ width: "100%" }} // ensures ListItemText stretches
								/>
							</ListItemButton>
						</React.Fragment>
					))}
				</List>
			</Box>
		</Box>
	)
}
