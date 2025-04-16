"use client"

import TableBody from "@mui/material/TableBody";
import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import { useEffect, useState } from "react";
import { easyFetch } from "@/utils/fetchWrapper"
import Box from "@mui/material/Box";

type Alerts = {
	studentOne: string,
	studentTwo: string,
	alertType: string
}
	
export default function Alerts() {
	const [alerts, setAlerts] = useState<Alerts[]>([{ studentOne:"John",studentTwo: "Tod", alertType:"Assignment"}]);

	// useEffect(() => {
	// 		const fetchSimiliarities = async () => {
	// 			try {
	// 				const response = await easyFetch(
	// 					"http://localhost:8000/api/cheating/submission-similiarity-pairs/",
	// 					{
	// 						method: "get",
	// 					}
	// 				)
	
	// 				const data = await response.json()
	
	// 				if (response.ok) {
	// 					setAlerts(data["results"])
	// 				}
	// 			} catch (error) {
	// 				console.error(error)
	// 			}
	// 		}
	
	// 		fetchSimiliarities()
	// 	}, [])

	return (
		<Box>
			<TableContainer component={Paper}>
				<Table sx={{ minWidth: 650 }} aria-label="alerts table">
					<TableHead>
						<TableRow>
							<TableCell>Student 1</TableCell>
							<TableCell>Student 2</TableCell>
							<TableCell>Alert Type</TableCell>
						</TableRow>
					</TableHead>
					<TableBody>
						{alerts.map((alert) => (
							<TableRow
								key={alert.studentOne + alert.studentTwo}
								sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
							>
								<TableCell>{alert.studentOne}</TableCell>
								<TableCell>{alert.studentTwo}</TableCell>
								<TableCell>{alert.alertType}</TableCell>
							</TableRow>
						))}
					</TableBody>
				</Table>
			</TableContainer>
		</Box>
	);
}
