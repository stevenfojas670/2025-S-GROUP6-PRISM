"use client"
import {
	Box,
	Card,
	CardHeader,
	CardActions,
	CardActionaArea,
	CardContent,
	Typography,
} from "@mui/material"

interface Props {
	children: React.ReactNode
}

export default function CourseCards({ children }: Props) {
	return (
		<Box
			sx={{
				width: 300,
				backgroundColor: "background.paper",
				borderRadius: "5px",
				justifyContent: "center",
				display: "flex",
				py: "10px",
			}}
		>
			{children}
		</Box>
	)
}
