/* 
    Variables: Class_Name, Section_Name, Display_Name
    Buttons: Menu, Student Comparison, Alerts, n boxes with Class_Names and Section_Names
    Links: Student Comparison Tool, Alerts, Each box
    Header takes Display_Name
*/

"use client"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Typography, Box } from "@mui/material"
import { GetSemesters } from "@/controllers/semesters"
import { useAuth } from "@/context/AuthContext"
import { Semester } from "@/types/semesterTypes"
import CustomCards from "@/components/CustomCards"
import DashboardSection from "@/components/DashboardSection"

export default function Dashboard() {
	const router = useRouter()
	const { user } = useAuth()
	const [semesters, setSemesters] = useState<Semester[]>([])
	const [loading, setLoading] = useState(true)

	useEffect(() => {
		const loadSemesters = async () => {
			const data = await GetSemesters(Number(user?.pk))
			if ("results" in data) {
				setSemesters(data.results)
			} else {
				console.error("Error fetching semesters: ", data)
			}
			setLoading(false)
		}
		loadSemesters()
	}, [user])

	return (
		<Box
			sx={(theme) => ({
				backgroundColor: theme.palette.background.paper,
				height: "100%",
				p: 2,
				display: "flex",
				flexDirection: "column",
				gap: 2,
			})}
		>
			{/* Rendering semesters */}
			<DashboardSection title="View your semesters">
				{loading ? (
					<Typography>Loading semesters...</Typography>
				) : (
					semesters.map((semester) => (
						<CustomCards
							key={semester.id}
							onClick={() => router.push(`/semesters/${semester.id}`)}
						>
							<Typography>{semester.name}</Typography>
						</CustomCards>
					))
				)}
			</DashboardSection>

			{/* View other options */}
			<DashboardSection title="Other options">
				<CustomCards onClick={() => router.push("/student_comparison")}>
					<Typography>Student Comparison</Typography>
				</CustomCards>
				<CustomCards onClick={() => router.push("/alerts")}>
					<Typography>Alerts</Typography>
				</CustomCards>
				<CustomCards onClick={() => router.push("/assignment_creation")}>
					<Typography>Assignment Creation</Typography>
				</CustomCards>
				<CustomCards onClick={() => router.push("/plagiarism_report")}>
					<Typography>Plagiarism Report</Typography>
				</CustomCards>
			</DashboardSection>
		</Box>
	)
}
