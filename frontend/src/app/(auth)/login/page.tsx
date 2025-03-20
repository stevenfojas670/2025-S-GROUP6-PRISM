import { Container, Typography } from "@mui/material"
import { SignInButton } from "@/components/AuthenticationMethod"
import { auth } from "@/lib/auth"
import { redirect } from "next/navigation"

export default async function Login() {
	const session = await auth()

	if (session) redirect("/dashboard")

	return (
		<Container>
			<Typography>Welcome to PRISM, please login below.</Typography>
			<SignInButton />
		</Container>
	)
}
