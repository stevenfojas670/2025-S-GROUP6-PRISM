"use client"

import { useState, useEffect } from "react"
import {
	Box,
	Typography,
	FormControl,
	InputLabel,
	Select,
	MenuItem,
	Button,
	TableContainer,
	Table,
	TableHead,
	TableRow,
	TableCell,
	TableBody,
	CircularProgress,
	Divider,
	Switch,
	FormControlLabel,
	Skeleton,
} from "@mui/material"
import { grey } from "@mui/material/colors"

import { useAuth } from "@/context/AuthContext"
import { GetSemesters } from "@/controllers/semesters"
import { GetCourses } from "@/controllers/courses"
import { GetAssignments } from "@/controllers/assignments"
import { GetSubmittedStudents } from "@/controllers/students"
import { GetSimilarityPairs } from "@/controllers/similarityPairs"

import { Semester } from "@/types/semesterTypes"
import { Course } from "@/types/coursesTypes"
import { AssignmentItem } from "@/types/assignmentTypes"
import { SimilarityPair } from "@/types/similarityTypes"
import { Student } from "@/types/studentTypes"

export default function StudentComparison() {
	const { user } = useAuth()

	const [semesters, setSemesters] = useState<Semester[]>([])
	const [semester, setSemester] = useState<number | null>(null)
	const [semester1, setSemester1] = useState<number | null>(null)
	const [semester2, setSemester2] = useState<number | null>(null)
	const [matchSemesters, setMatchSemesters] = useState(true)

	const [courses, setCourses] = useState<Course[]>([])
	const [course, setCourse] = useState<number | null>(null)
	const [course1, setCourse1] = useState<number | null>(null)
	const [course2, setCourse2] = useState<number | null>(null)
	const [matchCourses, setMatchCourses] = useState(true)

	const [assignments, setAssignments] = useState<AssignmentItem[]>([])
	const [assignmentId, setAssignmentId] = useState<number | null>(null)

	const [students, setStudents] = useState<Student[]>([])
	const [studentA, setStudentA] = useState<number | null>(null)
	const [studentB, setStudentB] = useState<number | null>(null)

	const [pageSize, setPageSize] = useState<number | null>(10)
	const [similarity, setSimilarity] = useState<SimilarityPair[] | null>(null)
	const [loading, setLoading] = useState(false)

	const handleClear = () => {
		setSemester(null)
		setSemester1(null)
		setSemester2(null)
		setMatchSemesters(true)

		setCourse(null)
		setCourse1(null)
		setCourse2(null)
		setMatchCourses(true)

		setAssignments([])
		setAssignmentId(null)

		setStudents([])
		setStudentA(null)
		setStudentB(null)

		setSimilarity(null)
	}

	const isCourseSelectionValid = () =>
		matchCourses ||
		(course1 !== null && course2 !== null && course1 !== course2)

	const isSemesterSelectionValid = () =>
		matchSemesters ||
		(semester1 !== null && semester2 !== null && semester1 !== semester2)

	const handleSemesterToggle = (e: React.ChangeEvent<HTMLInputElement>) => {
		const isChecked = e.target.checked
		setMatchSemesters(isChecked)

		setSemester1(null)
		setSemester2(null)
		setSemester(null)
	}

	const handleCourseToggle = (e: React.ChangeEvent<HTMLInputElement>) => {
		const isChecked = e.target.checked
		setMatchCourses(isChecked)

		setCourse1(null)
		setCourse2(null)
		setCourse(null)
	}

	useEffect(() => {
		if (user?.pk) {
			GetSemesters(user.pk).then((data) => {
				if ("results" in data) setSemesters(data.results)
			})
		}
	}, [user])

	useEffect(() => {
		if (user?.pk && semester) {
			GetCourses(user.pk, semester).then((data) => {
				if ("results" in data) setCourses(data.results)
			})
		}
	}, [semester, user])

	useEffect(() => {
		if (course) {
			GetAssignments(course, null, 100).then((data) => {
				if ("results" in data) setAssignments(data.results)
			})
		}
	}, [course])

	useEffect(() => {
		GetSubmittedStudents(course, assignmentId, semester, semester2).then(
			(data) => {
				if (Array.isArray(data)) setStudents(data)
			}
		)
	}, [course, assignmentId, semester, semester2])

	const fetchSimilarities = async () => {
		if (!assignmentId || (!studentA && !studentB)) return
		setLoading(true)

		const data = await GetSimilarityPairs(
			matchCourses ? course : null,
			!matchCourses ? course1 : null,
			!matchCourses ? course2 : null,
			studentA,
			studentB,
			assignmentId,
			matchSemesters ? semester : null,
			!matchSemesters ? semester1 : null,
			!matchSemesters ? semester2 : null,
			pageSize
		)

		if ("results" in data) {
			setSimilarity(data.results)
		} else {
			console.error("Error fetching similarities", data)
		}
		setLoading(false)
	}

	return (
		<Box
			sx={{
				display: "flex",
				gap: 1,
				width: "100%",
				height: "100%",
				maxHeight: "100%",
			}}
		>
			{/* Left Panel of the form inputs */}
			<Box
				sx={(theme) => ({
					width: "50%",
					display: "flex",
					flexDirection: "column",
					gap: 2,
					p: 2,
					backgroundColor: theme.palette.background.paper,
				})}
			>
				{/* Semester selection */}
				<Box>
					<Typography variant="h4" gutterBottom>
						Student Comparison
					</Typography>
					<Divider sx={{ mb: 2 }} />
					<Box sx={{ display: "flex", gap: 1 }}>
						<FormControl fullWidth>
							<InputLabel>
								{matchSemesters ? "Semester" : "First Semester"}
							</InputLabel>
							<Select
								value={matchSemesters ? semester ?? "" : semester1 ?? ""}
								onChange={(e) =>
									matchSemesters
										? setSemester(Number(e.target.value))
										: setSemester1(Number(e.target.value))
								}
								label="Semester"
							>
								{semesters.map((sem) => (
									<MenuItem key={sem.id} value={sem.id}>
										{sem.name}
									</MenuItem>
								))}
							</Select>
						</FormControl>
						{!matchSemesters && (
							<FormControl fullWidth>
								<InputLabel>Second Semester</InputLabel>
								<Select
									value={semester2 ?? ""}
									onChange={(e) => setSemester2(Number(e.target.value))}
									label="Second Semester"
								>
									{semesters.map((sem) => (
										<MenuItem key={sem.id} value={sem.id}>
											{sem.name}
										</MenuItem>
									))}
								</Select>
							</FormControl>
						)}
					</Box>
					{/* <FormControlLabel
						control={
							<Switch
								checked={matchSemesters}
								onChange={handleSemesterToggle}
							/>
						}
						label="Match Semesters"
					/> */}
					{!matchSemesters && semester1 === semester2 && semester1 !== null && (
						<Typography color="error" variant="caption">
							First and second semesters must be different.
						</Typography>
					)}
				</Box>
				{/* Course selection */}
				<Box>
					<Box sx={{ display: "flex", gap: 1 }}>
						<FormControl fullWidth>
							<InputLabel>
								{matchCourses ? "Course" : "First Course"}
							</InputLabel>
							<Select
								value={matchCourses ? course ?? "" : course1 ?? ""}
								onChange={(e) =>
									matchCourses
										? setCourse(Number(e.target.value))
										: setCourse1(Number(e.target.value))
								}
								label="Course"
							>
								{courses.map((c) => (
									<MenuItem key={c.id} value={c.id}>
										{c.course_catalog.name}
									</MenuItem>
								))}
							</Select>
						</FormControl>
						{!matchCourses && (
							<FormControl fullWidth>
								<InputLabel>Second Course</InputLabel>
								<Select
									value={course2 ?? ""}
									onChange={(e) => setCourse2(Number(e.target.value))}
									label="Second Course"
								>
									{courses.map((c) => (
										<MenuItem key={c.id} value={c.id}>
											{c.course_catalog.name}
										</MenuItem>
									))}
								</Select>
							</FormControl>
						)}
					</Box>
					{/* <FormControlLabel
						control={
							<Switch checked={matchCourses} onChange={handleCourseToggle} />
						}
						label="Match Courses"
					/> */}
					{!matchCourses && course1 === course2 && course1 !== null && (
						<Typography color="error" variant="caption">
							First and second courses must be different.
						</Typography>
					)}
				</Box>
				{/* Assignment selection */}
				<FormControl fullWidth disabled={!course}>
					<InputLabel>Assignment</InputLabel>
					<Select
						value={assignmentId ?? ""}
						onChange={(e) => setAssignmentId(Number(e.target.value))}
						label="Assignment"
					>
						{assignments.map((a) => (
							<MenuItem key={a.id} value={a.id}>
								{a.title}
							</MenuItem>
						))}
					</Select>
				</FormControl>
				{/* Student selections */}
				<FormControl fullWidth disabled={!course}>
					<InputLabel>Student A</InputLabel>
					<Select
						value={studentA ?? ""}
						onChange={(e) => setStudentA(Number(e.target.value))}
						label="Student A"
					>
						{students.map((s) => (
							<MenuItem key={s.id} value={s.id}>
								{s.first_name} {s.last_name}
							</MenuItem>
						))}
					</Select>
				</FormControl>

				<FormControl fullWidth disabled={!course}>
					<InputLabel>Student B</InputLabel>
					<Select
						value={studentB ?? ""}
						onChange={(e) => setStudentB(Number(e.target.value))}
						label="Student B"
					>
						{students.map((s) => (
							<MenuItem key={s.id} value={s.id}>
								{s.first_name} {s.last_name}
							</MenuItem>
						))}
					</Select>
				</FormControl>

				<Button variant="contained" onClick={fetchSimilarities}>
					{loading ? <CircularProgress size={24} /> : "Compare Students"}
				</Button>
				<Button variant="outlined" onClick={handleClear}>
					Clear
				</Button>
			</Box>
			{/* Right Panel of the similarity table */}
			<Box
				sx={(theme) => ({
					width: "50%",
					p: 2,
					backgroundColor: theme.palette.background.paper,
				})}
			>
				<TableContainer sx={{ backgroundColor: grey[100] }}>
					<Table>
						<TableHead>
							<TableRow>
								<TableCell>Students</TableCell>
								<TableCell>Similarity Score</TableCell>
							</TableRow>
						</TableHead>
						{similarity && (
							<TableBody>
								{similarity.map((pair) => (
									<TableRow key={pair.id}>
										<TableCell>
											{pair.submission_id_1.student.first_name}{" "}
											{pair.submission_id_1.student.last_name} &amp;{" "}
											{pair.submission_id_2.student.first_name}{" "}
											{pair.submission_id_2.student.last_name}
										</TableCell>
										<TableCell>{pair.percentage}%</TableCell>
									</TableRow>
								))}
							</TableBody>
						)}
					</Table>
				</TableContainer>
			</Box>
		</Box>
	)
}
