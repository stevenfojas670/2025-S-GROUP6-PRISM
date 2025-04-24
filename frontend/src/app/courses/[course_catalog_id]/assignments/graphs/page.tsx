"use client"

import {
	GetSimilarityIntervalPlot,
	GetDistributionPlot,
	GetSimilarityPlot,
} from "@/controllers/graphs"
import { Box, Typography } from "@mui/material"
import { useSearchParams } from "next/navigation"
import { useCourseContext } from "@/context/CourseContext"
import { useEffect, useState } from "react"

export default function Graphs() {
	const searchParams = useSearchParams()
	const assignmentIdParam = searchParams.get("assignment")
	const assignmentId = assignmentIdParam ? Number(assignmentIdParam) : null

	const { courseInstanceId, semesterId } = useCourseContext()

	const [similarityPlot, setSimilarityPlot] = useState<string>("")
	const [intervalPlot, setIntervalPlot] = useState<string>("")
	const [distributionPlot, setDistributionPlot] = useState<string>("")

	useEffect(() => {
		if (!assignmentId) return

		const fetchAllPlots = async () => {
			const [simPlot, intPlot, distPlot] = await Promise.all([
				GetSimilarityPlot(assignmentId),
				GetSimilarityIntervalPlot(assignmentId),
				GetDistributionPlot(assignmentId),
			])

			setSimilarityPlot(simPlot ?? "")
			setIntervalPlot(intPlot ?? "")
			setDistributionPlot(distPlot ?? "")
		}

		fetchAllPlots()
	}, [assignmentId])

	return (
		<Box>
			<Box
				sx={(theme) => ({
					backgroundColor: theme.palette.background.paper,
					p: 2,
					boxShadow: 2,
					overflowX: "auto",
				})}
			>
				<Typography variant="h6">Similarity Plot</Typography>
				<Box
					sx={{
						width: "100%",
						overflowX: "auto",
						mt: 1,
						border: "1px solid #ccc", // optional visual cue
						borderRadius: 2,
					}}
				>
					{similarityPlot ? (
						<Box
							component="img"
							src={similarityPlot}
							alt="Similarity Plot"
							sx={{
								height: "auto",
								width: "auto",
								maxWidth: "none",
							}}
						/>
					) : (
						<Typography variant="caption" sx={{ p: 2 }}>
							No Similarity Plot Available
						</Typography>
					)}
				</Box>

				<Typography variant="h6" sx={{ mt: 4 }}>
					Similarity Interval Plot
				</Typography>
				<Box
					sx={{
						width: "100%",
						mt: 1,
						maxHeight: 900, // ✅ set vertical height limit
						overflowY: "auto", // ✅ allow vertical scrolling
						border: "1px solid #ccc", // optional visual cue
						borderRadius: 2,
					}}
				>
					{intervalPlot ? (
						<Box
							component="img"
							src={intervalPlot}
							alt="Interval Plot"
							sx={{
								maxWidth: "none",
								objectFit: "contain",
							}}
						/>
					) : (
						<Typography variant="caption" sx={{ p: 2 }}>
							No Interval Plot Available
						</Typography>
					)}
				</Box>

				<Typography variant="h6" sx={{ mt: 4 }}>
					Distribution Plot
				</Typography>
				{distributionPlot ? (
					<Box
						component="img"
						src={distributionPlot}
						alt="Distribution Plot"
						sx={{
							height: 400,
							border: "1px solid #ccc", // optional visual cue
							borderRadius: 2,
						}}
					/>
				) : (
					<Typography variant="caption">
						No Distribution Plot Available
					</Typography>
				)}
			</Box>
		</Box>
	)
}
