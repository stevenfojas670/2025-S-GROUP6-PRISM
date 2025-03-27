"use client"
import { Container, Typography, Button } from "@mui/material"
import { SignOutButton } from "@/components/AuthenticationMethod"
import { useCallback, useEffect, useState } from "react"
import type { User } from "@/types/index"
import { easyFetch } from "@/utils/fetchWrapper"

export default function Dashboard() {
	const [users, setUsers] = useState<User[]>([])
	const [user, setUser] = useState<User | null>(null)
	const [loading, setLoading] = useState<Boolean>(false)

	const fetchMyself = useCallback(async () => {
		setLoading(true)
		try {
			const response = await easyFetch(
				"http://localhost:8000/api/user/users/me",
				{
					method: "get",
				}
			)

			const data = await response.json()

			if (response.ok) {
				setUser(data)
			} else {
				console.error("Failed to fetch user.")
			}
		} catch (err) {
			console.error(err)
		} finally {
			setLoading(false)
		}
	}, [])

	const fetchUsers = useCallback(async () => {
		setLoading(true)
		try {
			const response = await easyFetch(
				"http://localhost:8000/api/user/users/",
				{
					method: "get",
				}
			)

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
			<Button onClick={fetchMyself}>
				{loading ? "loading..." : "Fetch myself"}
			</Button>
			<Container>
				{user && (
					<ul>
						<li>{user.email}</li>
						<li>{user.first_name}</li>
						<li>{user.last_name}</li>
					</ul>
				)}
			</Container>
			<Container>
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
		</Container>
	)
}
