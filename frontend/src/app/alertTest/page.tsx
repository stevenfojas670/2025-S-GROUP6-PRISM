"use client"

import React, { useState } from "react"
import {
	Table,
	TableBody,
	TableCell,
	TableContainer,
	TableHead,
	TableRow,
	Paper,
	IconButton,
	Collapse,
	Box,
	Typography,
	Button,
	CircularProgress,
} from "@mui/material"
import {
	KeyboardArrowDown as ArrowDownIcon,
	KeyboardArrowUp as ArrowUpIcon,
	CheckCircleOutline as ResolvedIcon,
} from "@mui/icons-material"

// Simulated API call
const fetchAlertDetails = async (alertType: string) => {
	// Simulating API delay
	return new Promise((resolve) => {
		setTimeout(() => {
			resolve({
				info: `Detailed info for ${alertType}`,
				recommendation: `Recommended action for ${alertType}`,
			})
		}, 800)
	})
}

// Sample alert summary list (comes from your API, ideally)
const initialAlerts = [
	{ id: 1, type: "Plagiarism" },
	{ id: 2, type: "Late Submission" },
	{ id: 3, type: "Missing Files" },
]

type AlertDetail = {
	info: string
	recommendation: string
}

export default function FullExpandableAlertTable() {
	const [expandedRows, setExpandedRows] = useState<number[]>([])
	const [alertDetails, setAlertDetails] = useState<
		Record<number, AlertDetail | null>
	>({})
	const [loadingRows, setLoadingRows] = useState<number[]>([])
	const [resolvedRows, setResolvedRows] = useState<number[]>([])

	const toggleRow = async (rowId: number, alertType: string) => {
		const isOpen = expandedRows.includes(rowId)

		if (isOpen) {
			setExpandedRows((prev) => prev.filter((id) => id !== rowId))
		} else {
			setExpandedRows((prev) => [...prev, rowId])

			// Fetch alert details if not already loaded
			if (!alertDetails[rowId]) {
				setLoadingRows((prev) => [...prev, rowId])
				const details = await fetchAlertDetails(alertType)
				setAlertDetails((prev) => ({
					...prev,
					[rowId]: details as AlertDetail,
				}))
				setLoadingRows((prev) => prev.filter((id) => id !== rowId))
			}
		}
	}

	const markAsResolved = (rowId: number) => {
		setResolvedRows((prev) => [...prev, rowId])
	}

	return (
		<TableContainer component={Paper}>
			<Table>
				<TableHead>
					<TableRow>
						<TableCell />
						<TableCell>Alert Type</TableCell>
						<TableCell>Status</TableCell>
					</TableRow>
				</TableHead>
				<TableBody>
					{initialAlerts.map((alert) => (
						<React.Fragment key={alert.id}>
							<TableRow>
								<TableCell>
									<IconButton
										size="small"
										onClick={() => toggleRow(alert.id, alert.type)}
									>
										{expandedRows.includes(alert.id) ? (
											<ArrowUpIcon />
										) : (
											<ArrowDownIcon />
										)}
									</IconButton>
								</TableCell>
								<TableCell>{alert.type}</TableCell>
								<TableCell>
									{resolvedRows.includes(alert.id) ? (
										<Typography color="green">
											<ResolvedIcon fontSize="small" /> Resolved
										</Typography>
									) : (
										"Pending"
									)}
								</TableCell>
							</TableRow>

							<TableRow>
								<TableCell
									style={{ paddingBottom: 0, paddingTop: 0 }}
									colSpan={3}
								>
									<Collapse
										in={expandedRows.includes(alert.id)}
										timeout="auto"
										unmountOnExit
									>
										<Box margin={2}>
											{loadingRows.includes(alert.id) ? (
												<CircularProgress size={24} />
											) : (
												<>
													<Typography variant="body2" gutterBottom>
														<strong>Info:</strong>{" "}
														{alertDetails[alert.id]?.info}
													</Typography>
													<Typography variant="body2" gutterBottom>
														<strong>Recommendation:</strong>{" "}
														{alertDetails[alert.id]?.recommendation}
													</Typography>
													{!resolvedRows.includes(alert.id) && (
														<Button
															variant="contained"
															size="small"
															onClick={() => markAsResolved(alert.id)}
														>
															Mark as Resolved
														</Button>
													)}
												</>
											)}
										</Box>
									</Collapse>
								</TableCell>
							</TableRow>
						</React.Fragment>
					))}
				</TableBody>
			</Table>
		</TableContainer>
	)
}
