import { auth } from "@/lib/auth"
import { Container, Typography } from "@mui/material"
import { SignOutButton } from "@/components/AuthenticationMethod"
import { redirect } from "next/navigation"

export default async function Dashboard() {
	const session = await auth()

	if (!session) return redirect("/")

	return (
		<Container>
			<Typography>Welcome {session?.user?.name}</Typography>
			<SignOutButton />
		</Container>
	)
}
