import { easyFetch } from "@/utils/fetchWrapper"
import { StudentResponse } from "@/types/studentTypes"
import { APIError } from "@/types/APIError"

export async function GetStudents(
	uid: number,
	courseId: number
): Promise<StudentResponse | APIError> {
	try {
		const response = await easyFetch(
			`http://localhost:8000/api/course/courseinstances/get-all-students/?uid=${uid}&course=${courseId}&page_size=200`,
			{ method: "GET" }
		)

		const data = await response.json()

		if (response.ok) {
			return data.results as StudentResponse
		} else {
			return {
				detail: data.detail ?? "Failed to fetch students.",
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
