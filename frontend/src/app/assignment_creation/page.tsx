"use client"

import {
	Box,
	Button,
	FormControl,
	InputLabel,
	MenuItem,
	Select,
	TextField,
	Typography,
	Checkbox,
	FormControlLabel,
	Divider,
	SelectChangeEvent,
} from "@mui/material"
import { grey } from "@mui/material/colors"
import { SyntheticEvent, useEffect, useState } from "react"
import { useAuth } from "@/context/AuthContext"

// Controllers
import { GetAllCourses, GetCourses } from "@/controllers/courses"

// Types
import { Course } from "@/types/coursesTypes"
import { GetSemesters } from "@/controllers/semesters"
import { Semester } from "@/types/semesterTypes"
import { easyFetch } from "@/utils/fetchWrapper"

export default function AssignmentCreation() {
	const { user } = useAuth()
	const [loading, setLoading] = useState(true)
	const [semesters, setSemesters] = useState<Semester[]>([])
	const [courses, setCourses] = useState<Course[]>([])
	const [formData, setFormData] = useState({
		course_catalog: "",
		semester: "",
		assignment_number: "",
		title: "",
		due_date: "",
		lock_date: "",
		pdf_filepath: "",
		has_base_code: false,
		moss_report_directory_path: "",
		bulk_ai_directory_path: "",
		language: "",
		has_policy: false,
	})

	const [baseFiles, bfData] = useState({
		assignment: "",
		file_name: "",
		file_path: "",
	})

	const [requiredSubFiles, rsfData] = useState({
		assignment: "",
		file_name: "",
		similarity_threshold: "",
	})

	const [constraints, constraintData] = useState({
		assignment: "",
		identifier: "",
		is_library: "",
		is_keyword: "",
		is_permitted: "",
	})

	const handleChange = (
		e:
			| React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
			| SelectChangeEvent
	) => {
		const { name, type, value, checked } = e.target as HTMLInputElement
		setFormData((prev) => ({
			...prev,
			[name]: type === "checkbox" ? checked : value,
		}))
	}

	// Fetch semesters
	useEffect(() => {
		if (!user?.pk) return
		const fetchSemesters = async () => {
			setLoading(true)
			const data = await GetSemesters(user?.pk)

			if ("results" in data) {
				setSemesters(data.results)
			}
			setLoading(false)
		}
		fetchSemesters()
	}, [user?.pk])

	// Fetch courses
	useEffect(() => {
		if (!user?.pk || !formData.semester) return
		const fetchCourses = async () => {
			setLoading(true)
			const data = await GetCourses(user.pk, Number(formData.semester))

			if ("results" in data) {
				setCourses(data.results)
			}

			setLoading(false)
		}

		fetchCourses()
	}, [user?.pk, formData.semester])

	const handleSubmit = async () => {
		console.log("Submitting Assignment:", formData)

		const payload = {
			...formData,
			base_files: formData.has_base_code ? [baseFiles] : [],
			required_files: [requiredSubFiles],
			constraints: [constraints],
		}

		try {
			const response = await easyFetch(
				"http://localhost:8000/api/assignment/assignments/",
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify(payload),
				}
			)

			const result = await response.json()
			if (response.ok) {
				console.log("Assignment submitted!", result)
			} else {
				console.error("Submission failed:", result)
			}
		} catch (err) {
			console.error("Network error:", err)
		}
	}

	return (
		<Box
			sx={(theme) => ({
				p: 2,

				backgroundColor: theme.palette.background.paper,
			})}
		>
			<Typography variant="h4" gutterBottom>
				Create Assignment
			</Typography>
			<Divider sx={{ mb: 2 }} />
			<Box
				sx={(theme) => ({
					p: 2,
					display: "flex",
					flexDirection: "column",
					gap: 2, // or any spacing value, e.g., 3 or "16px"
					border: `1px solid ${theme.palette.background.default}`,
					boxShadow: 1,
				})}
			>
				<FormControl fullWidth>
					<InputLabel>Semester</InputLabel>
					<Select
						label="Semester"
						name="semester"
						value={formData.semester}
						onChange={handleChange}
					>
						{semesters.map((sem) => (
							<MenuItem key={sem.id} value={sem.id}>
								{sem.name}
							</MenuItem>
						))}
					</Select>
				</FormControl>
				<FormControl fullWidth disabled={!formData.semester}>
					<InputLabel>Course</InputLabel>
					<Select
						label="Course"
						name="course_catalog"
						value={formData.course_catalog}
						onChange={handleChange}
					>
						{courses.map((course) => (
							<MenuItem
								key={course.course_catalog.id}
								value={course.course_catalog.id}
							>
								{course.course_catalog.name}
							</MenuItem>
						))}
					</Select>
				</FormControl>

				<TextField
					label="Assignment Number"
					name="assignment_number"
					value={formData.assignment_number}
					type="number"
					onChange={handleChange}
					fullWidth
				/>

				<TextField
					label="Title"
					name="title"
					value={formData.title}
					onChange={handleChange}
					fullWidth
				/>

				<TextField
					label="Due Date"
					name="due_date"
					type="date"
					value={formData.due_date}
					onChange={handleChange}
					slotProps={{
						inputLabel: {
							shrink: true,
						},
					}}
					fullWidth
				/>

				<TextField
					label="Lock Date"
					name="lock_date"
					type="datetime-local"
					value={formData.lock_date}
					onChange={handleChange}
					slotProps={{
						inputLabel: {
							shrink: true,
						},
					}}
					fullWidth
				/>

				<TextField
					label="PDF Filepath"
					name="pdf_filepath"
					value={formData.pdf_filepath}
					onChange={handleChange}
					fullWidth
				/>
				<Box>
					<FormControlLabel
						control={
							<Checkbox
								name="has_base_code"
								checked={formData.has_base_code}
								onChange={handleChange}
							/>
						}
						label="Has Base Code"
					/>
				</Box>
				{formData.has_base_code && (
					<Box
						sx={(theme) => ({
							border: `1px solid ${theme.palette.background.default}`,
							p: 1,
							display: "flex",
							flexDirection: "column",
							gap: 2,
						})}
					>
						<TextField
							label="Base File Name"
							name="file_name"
							value={baseFiles.file_name}
							onChange={(e) =>
								bfData((prev) => ({ ...prev, file_name: e.target.value }))
							}
							fullWidth
						/>
						<TextField
							label="Base File Path"
							name="file_path"
							value={baseFiles.file_path}
							onChange={(e) =>
								bfData((prev) => ({ ...prev, file_path: e.target.value }))
							}
							fullWidth
						/>
					</Box>
				)}

				<TextField
					label="MOSS Report Directory"
					name="moss_report_directory_path"
					value={formData.moss_report_directory_path}
					onChange={handleChange}
					fullWidth
				/>

				<TextField
					label="Bulk AI Directory"
					name="bulk_ai_directory_path"
					value={formData.bulk_ai_directory_path}
					onChange={handleChange}
					fullWidth
				/>

				<TextField
					label="Language"
					name="language"
					value={formData.language}
					onChange={handleChange}
					fullWidth
				/>

				<Box>
					<FormControlLabel
						control={
							<Checkbox
								name="has_policy"
								checked={formData.has_policy}
								onChange={handleChange}
							/>
						}
						label="Has Policy"
					/>
				</Box>
				<Button>Add Contraints</Button>
				<Button variant="contained" onClick={handleSubmit}>
					Submit Assignment
				</Button>
			</Box>
		</Box>
	)
}
