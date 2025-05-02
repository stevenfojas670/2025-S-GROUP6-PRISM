import { easyFetch } from "@/utils/fetchWrapper"
import { CourseResponse } from "@/types/coursesTypes"
import { APIError } from "@/types/APIError"

export async function GetCourses(
	uid: number,
	semesterid: number
): Promise<CourseResponse | APIError> {
	try {
		const response = await easyFetch(
			`http://localhost:8000/api/course/courseinstances/get-courses-by-semesters/?uid=${uid}&semester=${semesterid}`,
			{ method: "GET" }
		)

		const data = await response.json()

		if (response.ok) {
			console.log(data)
			return data as CourseResponse
		} else {
			return {
				detail: data.detail ?? "Failed to fetch courses.",
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
