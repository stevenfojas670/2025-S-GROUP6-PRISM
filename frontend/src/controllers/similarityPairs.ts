import { easyFetch } from "@/utils/fetchWrapper"
import { SimilarityPairResponse } from "@/types/similarityTypes"
import { APIError } from "@/types/APIError"

export async function GetSimilarityPairs(
	course: number | null,
	course1: number | null,
	course2: number | null,
	student1: number | null,
	student2: number | null,
	assignment_id: number,
	semester: number | null,
	semester1: number | null,
	semester2: number | null,
	page_size: number | null
): Promise<SimilarityPairResponse | APIError> {
	try {
		const params = new URLSearchParams()

		if (course !== null) params.append("course", course.toString())
		if (course1 !== null) params.append("course1", course1.toString())
		if (course2 !== null) params.append("course2", course2.toString())
		if (student1 !== null) params.append("student1", student1.toString())
		if (student2 !== null) params.append("student2", student2.toString())
		if (assignment_id) params.append("asid", assignment_id.toString())
		if (semester !== null) params.append("semester", semester.toString())
		if (semester1 !== null) params.append("semester1", semester1.toString())
		if (semester2 !== null) params.append("semester2", semester2.toString())
		if (page_size !== null) params.append("page_size", page_size.toString())

		params.append("ordering", "-percentage")

		const url = `http://localhost:8000/api/cheating/submission-similarity-pairs/?${params.toString()}`

		const response = await easyFetch(url, { method: "GET" })
		const data = await response.json()

		if (response.ok) {
			return data as SimilarityPairResponse
		} else {
			return {
				detail: data.detail ?? "Failed to fetch similarity pairs.",
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
