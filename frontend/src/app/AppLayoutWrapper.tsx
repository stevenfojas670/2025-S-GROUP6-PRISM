"use client"

import { usePathname } from "next/navigation"
import { Box, AppBar, Toolbar, Typography, Button } from "@mui/material"
import { SignOutButton } from "@/components/AuthenticationMethod"
import LeftPanel from "@/components/LeftPanel"
import RightPanel from "@/components/RightPanel"

interface Props {
	children: React.ReactNode
}

export default function AppLayoutWrapper({ children }: Props) {
	const pathname = usePathname()
	const isAuthPage = pathname === "/login/"

	if (isAuthPage) return children

	return (
		<Box
			sx={{
				display: "flex",
				height: "100vh",
				flexDirection: "column",
				p: 2,
			}}
		>
			<AppBar position="static" sx={{ borderRadius: 1 }}>
				<Toolbar>
					<Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
						PRISM
					</Typography>
					<Button variant="outlined">
						<SignOutButton />
					</Button>
				</Toolbar>
			</AppBar>
			<Box sx={{ display: "flex", gap: 2, my: 4 }}>
				<LeftPanel />
				<Box
					sx={{
						flexGrow: 1,
						overflowY: "auto",
						borderRadius: 1,
						border: "1px solid white",
						p: 2,
					}}
				>
					{children}
				</Box>
				<RightPanel />
			</Box>
		</Box>
	)
}
