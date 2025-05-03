"use client"

import { useRouter } from "next/navigation"

export function SignOutButton() {
	const router = useRouter()
	return <span onClick={() => router.push("/logout")}>Sign Out</span>
}
