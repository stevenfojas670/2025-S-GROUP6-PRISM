"use client"
import React, { useEffect, useState } from "react"
import {
	Typography,
	Box,
	Button,
	List,
	ListItemButton,
	ListItemText,
	Table,
	TableBody,
	TableCell,
	TableContainer,
	TableHead,
	TableRow,
	Paper,
} from "@mui/material"
import { useParams, useRouter } from "next/navigation"
import { GetStudents } from "@/controllers/students"
import { GetAssignments } from "@/controllers/assignments"
import { AssignmentItem } from "@/types/assignmentTypes"
import { Student } from "@/types/studentTypes"
import { useAuth } from "@/context/AuthContext"

const columns: { key: keyof AssignmentItem; label: string }[] = [
	{ key: "title", label: "Title" },
	{ key: "assignment_number", label: "Number" },
	{ key: "due_date", label: "Due Date" },
	{ key: "lock_date", label: "Lock Date" },
]

export default function Assignments() {
	const router = useRouter()
	const { courseId } = useParams()
	const { user } = useAuth()
	const [assignments, setAssignments] = useState<AssignmentItem[]>([])
	const [students, setStudents] = useState<Student[]>([])

	useEffect(() => {
		if (!courseId || !user) return
		const fetchAssignments = async () => {
			const data = await GetAssignments(Number(courseId))

			if ("results" in data) {
				setAssignments(data.results)
			} else {
				console.error("Error fetching assignments: ", data)
			}
		}

		const fetchStudents = async () => {
			if (!courseId || !user) return
			const data = await GetStudents(Number(user.pk), Number(courseId))
			if (Array.isArray(data)) {
				setStudents(data)
			} else {
				console.error("Error fetching students.", data)
			}
		}

		fetchAssignments()
		fetchStudents()
	}, [courseId, user])

	return (
		<Box sx={{ display: "flex", gap: 2 }}>
			{/* Body Container */}
			<Box
				sx={(theme) => ({
					backgroundColor: theme.palette.background.paper,
					p: 2,
					boxShadow: 2,
					overflowX: "auto",
					width: "100%",
					height: "100%",
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
				<Box sx={{ overflowY: "auto", height: "100%" }}>
					<TableContainer component={Paper} elevation={3}>
						<Table>
							<TableHead>
								<TableRow>
									{columns.map((col) => (
										<TableCell key={col.key}>{col.label}</TableCell>
									))}
									<TableCell>Action</TableCell>
								</TableRow>
							</TableHead>
							<TableBody>
								{assignments.map((assignment) => (
									<TableRow key={assignment.id}>
										<TableCell>{assignment.title}</TableCell>
										<TableCell>{assignment.assignment_number}</TableCell>
										<TableCell>{assignment.due_date}</TableCell>
										<TableCell>{assignment.lock_date}</TableCell>
										<TableCell>
											<Button onClick={() => console.log("nothing")}>
												View
											</Button>
										</TableCell>
									</TableRow>
								))}
							</TableBody>
						</Table>
					</TableContainer>
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
									primary={`${student.first_name} ${student.last_name}`}
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
