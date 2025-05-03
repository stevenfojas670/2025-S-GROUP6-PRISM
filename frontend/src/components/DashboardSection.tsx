"use client"

import { Typography, Box, SxProps, Theme, Divider } from "@mui/material"

interface Props {
	title: string
	children: React.ReactNode
	sx?: SxProps<Theme>
}

export default function DashboardSection({ title, children, sx }: Props) {
	return (
		<Box sx={{ ...sx }}>
			<Typography variant="h4" gutterBottom>
				{title}
			</Typography>
			<Divider />
			<Box sx={{ display: "flex", gap: 1, flexWrap: "wrap", pt: 2 }}>
				{children}
			</Box>
		</Box>
	)
}
