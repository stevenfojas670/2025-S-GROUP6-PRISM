import { easyFetch } from "@/utils/fetchWrapper"
import { APIError } from "@/types/APIError"
import { Alert, AlertResponse } from "@/types/alertType"

export async function GetAlerts(): Promise<AlertResponse | APIError> {
	try {
		const response = await easyFetch(
			"http://localhost:8000/api/cheating/submission-similarity-pairs/",
			{ method: "GET" }
		)

		const data = await response.json()

		if (response.ok) {
			const newAlerts: Alert[] = []

			data.results.forEach((result: any) => {
				const newAlert: Alert = {
					studentOne: result.submissions.student,
					studentTwo: result.submissions.students.student, // fixed typo
					alertType: "Assignment",
				}

				newAlerts.push(newAlert) // fixed concat misuse
			})

			const alertResponse: AlertResponse = { alerts: newAlerts }
			return alertResponse
		} else {
			return {
				detail: data.detail ?? "Failed to fetch alerts.",
				status: response.status,
			}
		}
	} catch (e) {
		console.error(e)
		return {
			message: "Something went wrong during fetch.",
		}
	}
}
