"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/context/AuthContext"

export default function LogoutPage() {
	const router = useRouter()
	const context = useAuth()

	useEffect(() => {
		const logoutFlow = async () => {
			try {
				const response = await fetch("http://localhost:8000/api/logout", {
					method: "POST",
					credentials: "include",
				})

				const data = await response.json()

				if (response.ok) {
					context?.logout()
					console.log("Succesfully logged out of Django: ", data)
				} else {
					throw new Error("Error logging out of Django: ", data.details)
				}
				router.push("/login")
			} catch (err) {
				console.error(err)
				router.push("/error")
			}
		}

		logoutFlow()
	}, [router, context])

	return <p>Logging you out...</p>
}
