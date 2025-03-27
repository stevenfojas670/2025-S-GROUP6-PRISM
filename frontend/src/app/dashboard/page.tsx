"use client"
import { Container, Typography, Button } from "@mui/material"
import { SignOutButton } from "@/components/AuthenticationMethod"
import { useCallback, useEffect, useState } from "react"
import type { User } from "@/types/index"
import { easyFetch } from "@/utils/fetchWrapper"

export default function Dashboard() {
	const [users, setUsers] = useState<User[]>([])
	const [loading, setLoading] = useState<Boolean>(false)

	const fetchUsers = useCallback(async () => {
		setLoading(true)
		try {
			const response = await easyFetch("http://localhost:8000/api/user/users", {
				method: "get",
			})

			const data = await response.json()

			if (response.ok) {
				setUsers(data)
			} else {
				console.error("Failed to fetch users.")
			}
		} catch (err) {
			console.error(err)
		} finally {
			setLoading(false)
		}
	}, [])

	return (
		<Container>
			<SignOutButton />
			<Button onClick={fetchUsers}>
				{loading ? "loading..." : "Fetch Users"}
			</Button>
			{users.length > 0 && (
				<div>
					{users.map((user, index) => (
						<ul key={index}>
							<li>{user.email}</li>
							<li>{user.first_name}</li>
							<li>{user.last_name}</li>
						</ul>
					))}
				</div>
			)}
		</Container>
	)
}
