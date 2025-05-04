import { easyFetch } from "@/utils/fetchWrapper"
import { AssignmentResponse } from "@/types/assignmentTypes"
import { APIError } from "@/types/APIError"

export async function GetAssignments(
	courseId: number
): Promise<AssignmentResponse | APIError> {
	try {
		const response = await easyFetch(
			`http://localhost:8000/api/assignment/assignments/get-assignments-by-course/?course=${courseId}`,
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
		console.error(e)
		return {
			message: "Something went wrong during fetch.",
		}
	}
}
