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
		mode: "light",
		background: {
			default: "#dedede", // soft light background
			paper: "#ffffff", // white surface
		},
		primary: {
			main: "#277ee3", // bold blue
			contrastText: "#ffffff",
		},
		secondary: {
			main: "#5ad1ff", // neon aqua accent
			contrastText: "#000000",
		},
		text: {
			primary: "#1e293b", // slate-900
			secondary: "#64748b", // slate-500
		},
		error: {
			main: "#ef4444", // red-500
		},
		warning: {
			main: "#facc15", // yellow-400
		},
		success: {
			main: "#22c55e", // green-500
		},
		info: {
			main: "#60a5fa", // sky-400
		},
		divider: "rgba(0, 0, 0, 0.12)",
	palette: {
		mode: "light",
		background: {
			default: "#dedede", // soft light background
			paper: "#ffffff", // white surface
		},
		primary: {
			main: "#277ee3", // bold blue
			contrastText: "#ffffff",
		},
		secondary: {
			main: "#5ad1ff", // neon aqua accent
			contrastText: "#000000",
		},
		text: {
			primary: "#1e293b", // slate-900
			secondary: "#64748b", // slate-500
		},
		error: {
			main: "#ef4444", // red-500
		},
		warning: {
			main: "#facc15", // yellow-400
		},
		success: {
			main: "#22c55e", // green-500
		},
		info: {
			main: "#60a5fa", // sky-400
		},
		divider: "rgba(0, 0, 0, 0.12)",
	},
	typography: {
		fontFamily: roboto.style.fontFamily,
	},
	shape: {
		borderRadius: 10,
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
		MuiDivider: {
			styleOverrides: {
				root: {
					variants: [
						{
							style: {
								backgroundColor: "#cccccc",
							},
						},
					],
				},
			},
		},
	},
})

export default theme

