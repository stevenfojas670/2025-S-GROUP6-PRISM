import { easyFetch } from "@/utils/fetchWrapper"
import { Semester, SemesterResponse } from "@/types/semesterTypes"
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

export async function GetSemester(id: number): Promise<Semester[] | APIError> {
	try {
		const response = await easyFetch(
			`http://localhost:8000/api/course/semester?semester_id=${id}`,
			{ method: "GET" }
		)

		const data = await response.json()

		if (response.ok) {
			return data.results as Semester[]
		} else {
			return {
				detail: data.detail ?? "Failed to fetch semester.",
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
