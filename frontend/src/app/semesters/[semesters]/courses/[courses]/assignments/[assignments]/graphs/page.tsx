"use client"

import {
	GetSimilarityIntervalPlot,
	GetDistributionPlot,
	GetSimilarityPlot,
} from "@/controllers/graphs"
import { Box, Typography, Tab, Tabs, CircularProgress } from "@mui/material"
import { useParams } from "next/navigation"
import { useEffect, useState } from "react"

export default function Graphs() {
	const params = useParams()
	const semesterId = params.semesters
	const courseInstanceId = params.courses
	const assignmentId = params.assignments

	const [similarityPlot, setSimilarityPlot] = useState("")
	const [intervalPlot, setIntervalPlot] = useState("")
	const [distributionPlot, setDistributionPlot] = useState("")
	const [tabValue, setTabValue] = useState(0)

	// Individual image loading states
	const [similarityLoaded, setSimilarityLoaded] = useState(true)
	const [intervalLoaded, setIntervalLoaded] = useState(true)
	const [distributionLoaded, setDistributionLoaded] = useState(true)

	useEffect(() => {
		if (!assignmentId) return

		const fetchAllPlots = async () => {
			setSimilarityLoaded(true)
			setIntervalLoaded(true)
			setDistributionLoaded(true)
			const [sim, int, dist] = await Promise.all([
				GetSimilarityPlot(Number(assignmentId)),
				GetSimilarityIntervalPlot(Number(assignmentId)),
				GetDistributionPlot(Number(assignmentId)),
			])

			setSimilarityPlot(sim ?? "")
			setIntervalPlot(int ?? "")
			setDistributionPlot(dist ?? "")
		}
		setSimilarityLoaded(false)
		setIntervalLoaded(false)
		setDistributionLoaded(false)

		fetchAllPlots()
	}, [assignmentId, semesterId, courseInstanceId])

	const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
		setTabValue(newValue)
	}

	const renderImage = (
		src: string,
		alt: string,
		loaded: boolean,
		setLoaded: (val: boolean) => void
	) => (
		<Box
			sx={(theme) => ({
				mt: 2,
				width: "100%",
				height: "100%",
				border: "1px solid",
				borderColor: theme.palette.divider,
				overflow: "auto",
				textAlign: "center",
				p: 1,
			})}
		>
			{!loaded && <CircularProgress />}
			{src && (
				<img
					src={src}
					alt={alt}
					onLoad={() => setLoaded(true)}
					style={{
						display: loaded ? "block" : "none",
						maxWidth: "100%",
						margin: "auto",
						objectFit: "contain",
					}}
				/>
			)}
		</Box>
	)

	return (
		<Box
			sx={(theme) => ({
				width: "100%",
				overflow: "hidden",
				backgroundColor: theme.palette.background.paper,
				boxShadow: 2,
				p: 2,
			})}
		>
			<Tabs
				value={tabValue}
				onChange={handleTabChange}
				sx={{ borderBottom: "1px solid grey" }}
			>
				<Tab label="Similarity Plot" />
				<Tab label="Similarity Interval Plot" />
				<Tab label="Distribution Plot" />
			</Tabs>

			{tabValue === 0 &&
				(similarityPlot && similarityLoaded ? (
					renderImage(
						similarityPlot,
						"Similarity Plot",
						similarityLoaded,
						setSimilarityLoaded
					)
				) : (
					<Box
						sx={{
							position: "absolute",
							top: "50%",
							left: "50%",
							transform: "translate(-50%, -50%)",
						}}
					>
						<CircularProgress />
					</Box>
				))}

			{tabValue === 1 &&
				(intervalPlot && intervalLoaded ? (
					renderImage(
						intervalPlot,
						"Similarity Interval Plot",
						intervalLoaded,
						setIntervalLoaded
					)
				) : (
					<Box
						sx={{
							position: "absolute",
							top: "50%",
							left: "50%",
							transform: "translate(-50%, -50%)",
						}}
					>
						<CircularProgress />
					</Box>
				))}

			{tabValue === 2 &&
				(distributionPlot && distributionLoaded ? (
					renderImage(
						distributionPlot,
						"Distribution Plot",
						distributionLoaded,
						setDistributionLoaded
					)
				) : (
					<Box
						sx={{
							position: "absolute",
							top: "50%",
							left: "50%",
							transform: "translate(-50%, -50%)",
						}}
					>
						<CircularProgress />
					</Box>
				))}
		</Box>
	)
}
