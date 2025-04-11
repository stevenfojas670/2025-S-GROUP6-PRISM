import { easyFetch } from "@/utils/fetchWrapper"
import { Course, CourseCatalog, CourseResponse } from "@/types/coursesTypes"
import { APIError } from "@/types/APIError"

export async function GetCourses(
	id: number
): Promise<CourseResponse | APIError> {
	const queryParams = new URLSearchParams({
		semester_id: String(id),
	})

	try {
		const response = await easyFetch(
			`http://localhost:8000/api/course/courseinstances?${queryParams}`,
			{ method: "GET" }
		)

		const data = await response.json()

		if (response.ok) {
			return data as CourseResponse
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
