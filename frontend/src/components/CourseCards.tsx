import { Box } from "@mui/material"

interface Props {
	children: React.ReactNode
}

export default function CourseCards({ children }: Props) {
	return <Box>{children}</Box>
}
