import { easyFetch } from "@/utils/fetchWrapper"
import { SubmissionResponse } from "@/types/submissionTypes"
import { APIError } from "@/types/APIError"

export async function GetSubmissions(
	assignmentId?: number,
	courseId?: number,
	semesterId?: number,
	studentId?: number
): Promise<SubmissionResponse | APIError> {
	const queryParams = new URLSearchParams()

	if (assignmentId !== undefined)
		queryParams.append("asid", assignmentId.toString())
	if (courseId !== undefined) queryParams.append("course", courseId.toString())
	if (semesterId !== undefined)
		queryParams.append("semester", semesterId.toString())
	if (studentId !== undefined)
		queryParams.append("student", studentId.toString())

	try {
		const response = await easyFetch(
			`http://localhost:8000/api/assignment/submissions/?${queryParams.toString()}`,
			{ method: "GET" }
		)

		const data = await response.json()

		if (response.ok) {
			return data as SubmissionResponse
		} else {
			return {
				detail: data.detail ?? "Failed to fetch submissions.",
				status: response.status,
			}
		}
	} catch (error) {
		console.error(error)
		return {
			message: "An unexpected error occurred during fetch.",
		}
	}
}
