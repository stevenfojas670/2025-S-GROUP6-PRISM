import NextAuth from "next-auth"

const handler = NextAuth({
	// Auth Options go here
	providers: [
		// Providers go here
	],
})

export { handler as GET, handler as POST }
