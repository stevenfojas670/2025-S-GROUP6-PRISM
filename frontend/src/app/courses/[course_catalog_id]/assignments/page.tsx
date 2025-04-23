"use client"
import { useCallback, useEffect, useState } from "react"
import { Container, Typography, Button, Box } from "@mui/material"
import { easyFetch } from "@/utils/fetchWrapper"
import { useParams } from "next/navigation"
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
	const { course_catalog_id } = useParams()

	useEffect(() => {
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
			<Typography variant="h4" gutterBottom>
				Assignments
			</Typography>
			<Box sx={{ display: "flex" }}>
				<Box
					sx={{
						width: "250px",
						display: "flex",
						flexDirection: "column",
						gap: 1,
						paddingRight: 2,
					}}
				>
					{assignments.map((assignment) => (
						<Button
							key={assignment.id}
							variant="outlined"
							sx={{ justifyContent: "flex-start" }}
						>
							{assignment.title}
						</Button>
					))}
				</Box>
			</Box>
		</Box>
	)
}
