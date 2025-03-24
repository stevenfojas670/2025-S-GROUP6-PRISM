/**
 * This is a fetch api wrapper to assist with handling error 401 when a token expires.
 * It also includes credentials by default so every request we make to Django will be
 * sent with cookies.
 */

export async function easyFetch(
	url: string,
	options: RequestInit = {}
): Promise<Response> {
	// Fetching the original request
	let res = await fetch(url, {
		...options,
		credentials: "include",
	})

	// If the token is expired, we will attempt to refresh
	if (res.status === 401) {
		console.warn("Token expired. Trying to refresh...")

		// Attempting to refresh
		const refreshRes = await fetch("http://localhost:8000/api/token/refresh", {
			method: "post",
			credentials: "include",
		})

		// If refresh was good, then we'll try the first request
		if (refreshRes.ok) {
			console.log("Token refreshed, retrying original request...")
			res = await fetch(url, {
				...options,
				credentials: "include",
			})
		} else {
			// Otherwise we'll go back to login
			console.error("Refresh failed. Logging out.")
			window.location.href = "/login"
			throw new Error("Unauthorized")
		}
	}

	return res
}
