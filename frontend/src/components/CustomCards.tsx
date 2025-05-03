"use client"
import { ButtonBase } from "@mui/material"
import { darken } from "@mui/material/styles"

interface Props {
	children: React.ReactNode
	onClick?: () => void
}

export default function CustomCards({ children, onClick }: Props) {
	return (
		<ButtonBase
			onClick={onClick}
			sx={(theme) => ({
				width: 200,
				height: 200,
				borderRadius: "10px",
				border: `1px solid ${theme.palette.background.default}`,
				overflow: "hidden",
				display: "block",
				textAlign: "center",
				px: 2,
				py: 3,
				// boxShadow: 2,
				transition: "background-color 0.3s ease",
				backgroundColor: theme.palette.background.paper,
				":hover": {
					backgroundColor: darken(theme.palette.background.paper, 0.05),
				},
			})}
		>
			{children}
		</ButtonBase>
	)
}
