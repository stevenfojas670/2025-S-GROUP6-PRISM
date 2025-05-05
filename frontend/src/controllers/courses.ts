import { easyFetch } from "@/utils/fetchWrapper"
import { CourseResponse } from "@/types/coursesTypes"
import { APIError } from "@/types/APIError"

export async function GetCourses(
	uid: number,
	semesterId: number,
	page?: number | null,
	page_size?: number | null
): Promise<CourseResponse | APIError> {
	try {
		const queryParams = new URLSearchParams({
			uid: String(uid),
			semester: String(semesterId),
		})

		if (page !== null && page !== undefined)
			queryParams.append("page", String(page))
		if (page_size !== null && page_size !== undefined)
			queryParams.append("page_size", String(page_size))

		const response = await easyFetch(
			`http://localhost:8000/api/course/courseinstances/get-courses-by-semesters/?${queryParams.toString()}`,
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

export async function GetAllCourses(
	uid: number
): Promise<CourseResponse | APIError> {
	try {
		const response = await easyFetch(
			`http://localhost:8000/api/course/courseinstances/get-all-courses/
			?uid=${uid}`,
			{ method: "GET" }
		)

		const data = await response.json()

		if (response.ok) {
			console.log(data)
			return data as CourseResponse
		} else {
			return {
				detail: data.detail ?? "Failed to fetch all courses.",
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
