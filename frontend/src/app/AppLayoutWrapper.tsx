"use client"

import { useAuth } from "@/context/AuthContext"
import { Box, AppBar, Toolbar, Typography, Button, Link } from "@mui/material"
import { useRouter } from "next/navigation"
import { SignOutButton } from "@/components/AuthenticationMethod"
import LeftPanel from "@/components/LeftPanel"

interface Props {
	children: React.ReactNode
}

export default function AppLayoutWrapper({ children }: Props) {
	const { user, loading } = useAuth()
	const router = useRouter()

	if (loading) return null

	if (!user?.isLoggedIn) {
		return children
	}
	return (
		<Box
			sx={{
				display: "flex",
				height: "100vh",
				flexDirection: "column",
			}}
		>
			<AppBar
				position="static"
				sx={(theme) => ({
					backgroundColor: theme.palette.background.paper,
					color: theme.palette.text.primary,
					zIndex: 100,
				})}
			>
				<Toolbar>
					<Box sx={{ flexGrow: 1 }}>
						<Link
							href="/dashboard"
							style={{ textDecoration: "none", color: "inherit" }}
						>
							<Typography
								variant="h6"
								component="div"
								sx={{ display: "flex", alignItems: "center", gap: 1 }}
							>
								PRISM
								<Box
									component="img"
									src="/prism_logo_transparent.png"
									alt="PRISM Logo"
									sx={{ width: 30, height: 30 }}
								/>
							</Typography>
						</Link>
					</Box>
					<Button variant="contained">
						<SignOutButton />
					</Button>
				</Toolbar>
			</AppBar>
			<Box
				sx={{
					display: "flex",
					height: "100%",
					overflow: "hidden",
				}}
			>
				<LeftPanel />
				<Box
					sx={{
						flexGrow: 1,
						overflow: "auto",
						p: 1,
					}}
				>
					{children}
				</Box>
			</Box>
		</Box>
	)
}
