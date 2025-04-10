"use client"

import { ReactNode } from "react"
import { AppBar, Toolbar, Typography, Container, Box } from "@mui/material"
import { SignOutButton } from "./AuthenticationMethod"

type LayoutProps = {
	children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
	return (
		<Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
			<AppBar position="static">
				<Toolbar>
					<Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
						Prism
					</Typography>
					<SignOutButton />
				</Toolbar>
			</AppBar>

			<Container sx={{ flex: 1, py: 4 }}>{children}</Container>

			<Box component="footer" sx={{ py: 2, textAlign: "center" }}>
				<Typography variant="body2">© 2025 Your App</Typography>
			</Box>
		</Box>
	)
}
