"use client"
import { useCallback, useEffect, useState } from "react"
import { Container, Typography, Button, Box } from "@mui/material"
import { easyFetch } from "@/utils/fetchWrapper"

interface AssignmentResposne {
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
	useEffect(() => {
		const fetchAssignments = async () => {
			try {
				const queryParams = new URLSearchParams({
					course_instance: String(3),
				})

				const response = await easyFetch(
					`http://localhost:8000/api/assignment/assignments?${queryParams}`,
					{
						method: "get",
					}
				)

				const data = await response.json()

				if (response.ok) {
					console.log("Good response")

					setAssignments(data.results)
				}
			} catch (error) {
				console.error(error)
			}
		}

		fetchAssignments()
	}, [])

	const [assignments, setAssignments] = useState<AssignmentItem[]>([])

	return (
		<Box>
			<Typography>Assignments</Typography>
			<Container>
				{assignments.map((assignment) => (
					<Button key={assignment.id}>{assignment.title}</Button>
				))}
			</Container>
		</Box>
	)
}
