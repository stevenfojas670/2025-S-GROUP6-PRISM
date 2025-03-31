"use client"
import { useCallback, useEffect, useState } from "react"
import { Container, Typography } from "@mui/material"

export default function Assignments() {
	useEffect(() => {
		const fetchAssignments = async () => {
			try {
				const response = await fetch(
					"http://localhost:8000/api/assignment/assignments",
					{
						method: "get",
					}
				)

				const data = await response.json()

				if (response.ok) {
					console.log("Good response")

					setAssignments(data)
				}
			} catch (error) {
				console.error(error)
			}
		}

		fetchAssignments()
	}, [])

	const [assignments, setAssignments] = useState<any[]>([])

	return (
		<Container>
			<Typography>Assignments</Typography>
			<Container>
				{assignments.map((assignment, index) => (
					<Container key={index} sx={{ mb: 3 }}>
						<Typography>Assignment ID: {assignment.id}</Typography>
						<Typography>
							Assignment Number: {assignment.assignment_number}
						</Typography>
						<Typography>Title: {assignment.title}</Typography>
						<Typography>Due Date: {assignment.due_date}</Typography>
					</Container>
				))}
			</Container>
		</Container>
	)
}
