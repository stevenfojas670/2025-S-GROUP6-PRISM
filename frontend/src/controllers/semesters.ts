import { easyFetch } from "@/utils/fetchWrapper"
import { SemesterResponse } from "@/types/semesterTypes"
import { APIError } from "@/types/APIError"

export async function GetSemesters(
	uid: number
): Promise<SemesterResponse | APIError> {
	try {
		const response = await easyFetch(
			`http://localhost:8000/api/course/semester/get-semesters/?uid=${uid}`,
			{ method: "GET" }
		)

		const data = await response.json()

		if (response.ok) {
			return data as SemesterResponse
		} else {
			return {
				detail: data.detail ?? "Failed to fetch semesters.",
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
