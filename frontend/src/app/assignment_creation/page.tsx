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
import { useState } from "react"

export default function AssignmentCreation() {
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

	const handleChange = (
		e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
	) => {
		const { name, value, type, checked } = e.target
		setFormData((prev) => ({
			...prev,
			[name]: type === "checkbox" ? checked : value,
		}))
	}

	const handleSubmit = async () => {
		// POST formData to your backend endpoint
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
				{/* Replace these dropdowns with actual fetched options */}
				<FormControl fullWidth>
					<InputLabel>Course Catalog</InputLabel>
					<Select
						name="course_catalog"
						value={formData.course_catalog}
						onChange={handleChange}
						label="Course Catalog"
					>
						<MenuItem value="1">CS 135</MenuItem>
						<MenuItem value="2">CS 202</MenuItem>
					</Select>
				</FormControl>

				<FormControl fullWidth>
					<InputLabel>Semester</InputLabel>
					<Select
						name="semester"
						value={formData.semester}
						onChange={handleChange}
						label="Semester"
					>
						<MenuItem value="1">Spring 2024</MenuItem>
						<MenuItem value="2">Fall 2024</MenuItem>
					</Select>
				</FormControl>

				<TextField
					label="Assignment Number"
					name="assignment_number"
					value={formData.assignment_number}
					onChange={handleChange}
					type="number"
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
					fullWidth
					InputLabelProps={{ shrink: true }}
				/>

				<TextField
					label="Lock Date"
					name="lock_date"
					type="datetime-local"
					value={formData.lock_date}
					onChange={handleChange}
					fullWidth
					InputLabelProps={{ shrink: true }}
				/>

				<TextField
					label="PDF Filepath"
					name="pdf_filepath"
					value={formData.pdf_filepath}
					onChange={handleChange}
					fullWidth
				/>

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

				<Button variant="contained" onClick={handleSubmit}>
					Submit Assignment
				</Button>
			</Box>
		</Box>
	)
}
