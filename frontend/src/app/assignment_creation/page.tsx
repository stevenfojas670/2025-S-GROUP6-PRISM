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
} from "@mui/material"
import { useEffect, useState } from "react"
import { useAuth } from "@/context/AuthContext"

// Controllers
import { GetAllCourses, GetCourses } from "@/controllers/courses"

// Types
import { Course } from "@/types/coursesTypes"

export default function AssignmentCreation() {
	const { user } = useAuth()

	const [courses, setCourses] = useState<Course[]>([])
	const [semesterId, setSemesterId] = useState<number | null>(null)
	const [formData, setFormData] = useState({
		course: "",
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

	// Fetch courses
	useEffect(() => {
		if (!user?.pk) return
		GetCourses(Number(user?.pk), Number(semesterId)).then((data) => {
			if ("results" in data) setCourses(data.results)
		})
	}, [user?.pk])

	const handleSubmit = async () => {
		console.log("Submitting Assignment:", formData)
		// Add actual POST logic here
	}

	return (
		<Box sx={{ p: 3 }}>
			<Typography variant="h4" gutterBottom>
				Create Assignment
			</Typography>
			<Divider sx={{ mb: 2 }} />
			<Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
				<FormControl fullWidth>
					<InputLabel>Course</InputLabel>
					<Select name="course" value={formData.course} label="Course">
						{courses.map((course) => (
							<MenuItem key={course.id}>{course.course_catalog.name}</MenuItem>
						))}
						<MenuItem value="1">CS 135</MenuItem>
						<MenuItem value="2">CS 202</MenuItem>
					</Select>
				</FormControl>

				<TextField
					label="Assignment Number"
					name="assignment_number"
					value={formData.assignment_number}
					type="number"
					fullWidth
				/>

				<TextField
					label="Title"
					name="title"
					value={formData.title}
					fullWidth
				/>

				<TextField
					label="Due Date"
					name="due_date"
					type="date"
					value={formData.due_date}
					fullWidth
					InputLabelProps={{ shrink: true }}
				/>

				<TextField
					label="Lock Date"
					name="lock_date"
					type="datetime-local"
					value={formData.lock_date}
					fullWidth
					InputLabelProps={{ shrink: true }}
				/>

				<TextField
					label="PDF Filepath"
					name="pdf_filepath"
					value={formData.pdf_filepath}
					fullWidth
				/>

				<FormControlLabel
					control={
						<Checkbox name="has_base_code" checked={formData.has_base_code} />
					}
					label="Has Base Code"
				/>

				<TextField
					label="MOSS Report Directory"
					name="moss_report_directory_path"
					value={formData.moss_report_directory_path}
					fullWidth
				/>

				<TextField
					label="Bulk AI Directory"
					name="bulk_ai_directory_path"
					value={formData.bulk_ai_directory_path}
					fullWidth
				/>

				<TextField
					label="Language"
					name="language"
					value={formData.language}
					fullWidth
				/>

				<FormControlLabel
					control={<Checkbox name="has_policy" checked={formData.has_policy} />}
					label="Has Policy"
				/>

				<Button variant="contained" onClick={handleSubmit}>
					Submit Assignment
				</Button>
			</Box>
		</Box>
	)
}
