import { easyFetch } from "@/utils/fetchWrapper"
import { AssignmentResponse } from "@/types/assignmentTypes"
import { APIError } from "@/types/APIError"

export async function GetAssignments(
	courseId: number,
	page?: number | null,
	page_size?: number | null
): Promise<AssignmentResponse | APIError> {
	try {
		const queryParams = new URLSearchParams({ course: String(courseId) })
		if (page !== null && page !== undefined) {
			queryParams.append("page", String(page))
		}
		if (page_size !== null && page_size !== undefined) {
			queryParams.append("page_size", String(page_size))
		}

		const response = await easyFetch(
			`http://localhost:8000/api/assignment/assignments/get-assignments-by-course/?${queryParams.toString()}`,
			{ method: "GET" }
		)

		const data = await response.json()

		if (response.ok) {
			return data as AssignmentResponse
		} else {
			return {
				detail: data.detail ?? "Failed to fetch assignments.",
				status: response.status,
			}
		}
	} catch (e) {
		console.error("Assignment fetch error:", e)
		return {
			message: "Something went wrong during fetch.",
		}
	}
}
