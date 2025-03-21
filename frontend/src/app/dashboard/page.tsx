import { Container, Typography } from "@mui/material"
import { auth } from "@/lib/auth"
import { redirect } from "next/navigation"
import { SignOutButton } from "@/components/AuthenticationMethod"

export default async function Dashboard() {
	const session = await auth() // Gets user session

	if (!session) return redirect("/login") // Checks if the session is valid and will redirect if not

	return (
		<Container>
			<Typography>Welcome {session?.user?.name}</Typography>
			<SignOutButton />
		</Container>
	)
}
