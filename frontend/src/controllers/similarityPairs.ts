import { easyFetch } from "@/utils/fetchWrapper"
import { SimilarityPairResponse } from "@/types/similarityTypes"
import { APIError } from "@/types/APIError"

export async function GetSimilarityPairs(
	assignment_id: number,
	course?: number | null,
	course1?: number | null,
	course2?: number | null,
	student1?: number | null,
	student2?: number | null,
	semester?: number | null,
	semester1?: number | null,
	semester2?: number | null,
	page_size?: number | null,
	page?: number | null
): Promise<SimilarityPairResponse | APIError> {
	try {
		const params = new URLSearchParams()

		if (course !== null && course !== undefined)
			params.append("course", course.toString())
		if (assignment_id) params.append("asid", assignment_id.toString())
		if (course1 !== null && course1 !== undefined)
			params.append("course1", course1.toString())
		if (course2 !== null && course2 !== undefined)
			params.append("course2", course2.toString())
		if (student1 !== null && student1 !== undefined)
			params.append("student1", student1.toString())
		if (student2 !== null && student2 !== undefined)
			params.append("student2", student2.toString())
		if (semester !== null && semester !== undefined)
			params.append("semester", semester.toString())
		if (semester1 !== null && semester1 !== undefined)
			params.append("semester1", semester1.toString())
		if (semester2 !== null && semester2 !== undefined)
			params.append("semester2", semester2.toString())
		if (page_size !== null && page_size !== undefined)
			params.append("page_size", page_size.toString())
		if (page !== null && page !== undefined)
			params.append("page", page.toString())

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
