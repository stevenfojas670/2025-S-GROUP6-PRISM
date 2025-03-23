"use client"
import { useRouter } from "next/router"

export default async function Home() {
	const router = useRouter()
	router.push("/login")
	return null
}
