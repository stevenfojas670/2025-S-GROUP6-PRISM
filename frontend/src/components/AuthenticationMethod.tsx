"use client"
import { Button } from "@mui/material"
import { signIn, signOut } from "next-auth/react"

export function SignInButton() {
	return (
		<Button onClick={() => signIn("google", { callbackUrl: "/dashboard" })}>
			Sign In
		</Button>
	)
}

export function SignOutButton() {
	return (
		<Button onClick={() => signOut({ callbackUrl: "/login" })}>Sign Out</Button>
	)
}
