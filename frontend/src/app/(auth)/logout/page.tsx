"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function LogoutPage() {
	const router = useRouter()

	useEffect(() => {
		const logoutFlow = async () => {
			try {
				const response = await fetch("http://localhost:8000/api/logout", {
					method: "POST",
					credentials: "include",
				})

				const data = await response.json()

				if (response.ok) {
					console.log("Succesfully logged out of Django: ", data)
				}
				// else { *This is mainly for testing, if logout fails, who cares, just go back to login
				// 	throw new Error("Error logging out of Django: ", data)
				// }
				router.push("/login")
			} catch (err) {
				console.error(err)
				router.push("/error")
			}
		}

		logoutFlow()
	}, [])

	return <p>Logging you out...</p>
}
