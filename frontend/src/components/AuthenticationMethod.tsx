"use client"
import { signIn } from "next-auth/react"
import { useRouter } from "next/navigation"
import Button from "@mui/material/Button"

export function SignInButton() {
	return (
		<span
			onClick={() =>
				signIn("google", { callbackUrl: "http://localhost:3000/callback" })
			}
		>
			Sign In with Google
		</span>
	)
}

export function SignOutButton() {
	const router = useRouter()

	return <span onClick={() => router.push("/logout")}>Sign Out</span>
}
