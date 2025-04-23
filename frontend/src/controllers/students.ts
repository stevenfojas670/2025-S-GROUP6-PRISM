import { easyFetch } from "@/utils/fetchWrapper"
import {
	Student,
	StudentEnrollments,
	StudentEnrollmentsResponse,
} from "@/types/studentTypes"
import { APIError } from "@/types/APIError"

export async function GetStudents(
	course_instance_id: number
): Promise<StudentEnrollmentsResponse | APIError> {
	const queryParams = new URLSearchParams({
		course_instance: String(course_instance_id),
	})

	try {
		const response = await easyFetch(
			`http://localhost:8000/api/course/studentenrollments/?${queryParams}`,
			{ method: "GET" }
		)

		const data = await response.json()

		if (response.ok) {
			return data as StudentEnrollmentsResponse
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
