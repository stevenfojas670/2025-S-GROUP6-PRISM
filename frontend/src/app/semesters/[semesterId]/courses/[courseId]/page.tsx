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
	LinearProgress,
	Divider,
	TablePagination,
} from "@mui/material"
import { useParams } from "next/navigation"
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
	const { courseId } = useParams()
	const { user } = useAuth()

	const [loading, setLoading] = useState(true)
	const [assignments, setAssignments] = useState<AssignmentItem[]>([])
	const [students, setStudents] = useState<Student[]>([])
	const [assignmentCurPage, setAssignmentCurPage] = useState(1) // 1-based for backend
	const [assignmentPageSize, setAssignmentPageSize] = useState(10) // matches backend default
	const [assignmentCount, setAssignmentCount] = useState(0)

	const page = assignmentCurPage - 1 // convert to 0-based index for MUI
	const emptyRows =
		page > 0
			? Math.max(0, (1 + page) * assignmentPageSize - assignmentCount)
			: 0

	useEffect(() => {
		if (!courseId || !user) return
		const fetchAssignments = async () => {
			setLoading(true)
			const data = await GetAssignments(
				Number(courseId),
				assignmentCurPage,
				assignmentPageSize
			)

			if ("results" in data) {
				setAssignments(data.results)
				setAssignmentCount(data.count)
				setAssignmentCurPage(data.current_page)
				setAssignmentPageSize(data.page_size)
				console.log(assignmentCurPage)
			} else {
				console.error("Error fetching assignments: ", data)
			}
			setLoading(false)
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
	}, [courseId, user, assignmentCurPage, assignmentPageSize])

	return (
		<Box
			sx={{ display: "flex", gap: 1, maxHeight: "100%", overflow: "hidden" }}
		>
			{/* Main Content */}
			<Box
				sx={(theme) => ({
					backgroundColor: theme.palette.background.paper,
					p: 2,
					boxShadow: 2,
					flex: 1,
					display: "flex",
					flexDirection: "column",
					minHeight: "100%",
				})}
			>
				{/* Page buttons */}
				<Box sx={{ display: "flex", gap: 2, mb: 2 }}>
					<Button variant="contained">Upload Assignment</Button>
					<Button variant="contained">Export All</Button>
				</Box>
				<Divider sx={{ mb: 2 }} />
				{/* Assignments Table */}
				{loading ? (
					<Box sx={{ width: "100%" }}>
						<LinearProgress />
					</Box>
				) : (
					<>
						<Box sx={{ flex: 1, overflow: "auto" }}>
							<TableContainer sx={{ maxHeight: "100%" }}>
								<Table size="small" stickyHeader>
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
											<TableRow hover key={assignment.id}>
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
										{emptyRows > 0 && (
											<TableRow style={{ height: 53 * emptyRows }}>
												<TableCell colSpan={columns.length + 1} />
											</TableRow>
										)}
									</TableBody>
								</Table>
							</TableContainer>
						</Box>
						<TablePagination
							rowsPerPageOptions={[10, 25, 50, 100, 150, 200]}
							component="div"
							count={assignmentCount}
							rowsPerPage={assignmentPageSize}
							page={page}
							onPageChange={(_, newPage) => {
								setAssignmentCurPage(newPage + 1)
							}}
							onRowsPerPageChange={(e) => {
								setAssignmentPageSize(parseInt(e.target.value, 10))
								setAssignmentCurPage(1)
							}}
						/>
					</>
				)}
			</Box>

			{/* Student Sidebar */}
			<Box
				sx={(theme) => ({
					width: 300,
					backgroundColor: theme.palette.background.paper,
					boxShadow: 2,
					p: 2,
					flexShrink: 0,
					overflowY: "auto",
					maxHeight: "100%",
				})}
			>
				<Typography variant="h6" gutterBottom>
					Students
				</Typography>
				<Divider />
				<List dense>
					{students.map((student) => (
						<ListItemButton key={student.id}>
							<ListItemText
								primary={`${student.first_name} ${student.last_name}`}
							/>
						</ListItemButton>
					))}
				</List>
			</Box>
		</Box>
	)
}
