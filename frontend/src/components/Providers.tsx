"use client"

import { SessionProvider } from "next-auth/react"
import { ThemeProvider } from "@mui/material/styles"
import AuthProvider from "@/context/AuthContext"
import CssBaseline from "@mui/material/CssBaseline"
import theme from "../theme"

export default function Providers({ children }: { children: React.ReactNode }) {
	return (
		<AuthProvider>
			<SessionProvider>
				<ThemeProvider theme={theme}>
					<CssBaseline />
					{children}
				</ThemeProvider>
			</SessionProvider>
		</AuthProvider>
	)
}
