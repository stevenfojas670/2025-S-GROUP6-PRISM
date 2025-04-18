"use client"
import { createTheme } from "@mui/material/styles"
import { Roboto } from "next/font/google"

const roboto = Roboto({
	weight: ["300", "400", "500", "700"],
	subsets: ["latin"],
	display: "swap",
})

const theme = createTheme({
	palette: {
		mode: "dark",
		background: {
			default: "#0a0a0a", // true black background
			paper: "#161616", // slightly lighter surface
		},
		primary: {
			main: "#0fffc1", // neon aqua
			contrastText: "#0a0a0a",
		},
		secondary: {
			main: "#ff5af1", // electric pink
			contrastText: "#0a0a0a",
		},
		text: {
			primary: "#f8f8f8", // bright white
			secondary: "#94a3b8", // steel gray
		},
		error: {
			main: "#ff4d4d", // bright red
		},
		warning: {
			main: "#facc15", // neon yellow
		},
		success: {
			main: "#6ee7b7", // mint green
		},
		info: {
			main: "#5ad1ff", // neon sky blue
		},
		divider: "rgba(255, 255, 255, 0.08)",
	},
	typography: {
		fontFamily: roboto.style.fontFamily,
	},
	shape: {
		borderRadius: 10,
	},
	components: {
		MuiAlert: {
			styleOverrides: {
				root: {
					variants: [
						{
							props: { severity: "info" },
							style: {
								backgroundColor: "#60a5fa",
							},
						},
					],
				},
			},
		},
	},
})

export default theme
