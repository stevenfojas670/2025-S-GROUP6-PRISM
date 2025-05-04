import { Box } from "@mui/material"

export default function RightPanel() {
	return (
		<Box
			sx={(theme) => ({
				backgroundColor: theme.palette.secondary.main,
				width: 200,
				minWidth: 150,
				p: 1,
			})}
		>
			Right Panel
		</Box>
	)
}
