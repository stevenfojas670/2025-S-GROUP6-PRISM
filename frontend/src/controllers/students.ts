import { easyFetch } from "@/utils/fetchWrapper"
import { StudentResponse, Student } from "@/types/studentTypes"
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

export async function GetSubmittedStudents(
	assignmentId: number | null,
	course?: number | null,
	semester?: number | null,
	semester1?: number | null
): Promise<Student[] | APIError> {
	const params = new URLSearchParams()
	if (course !== null && course !== undefined)
		params.append("course", course.toString())
	if (assignmentId) params.append("asid", assignmentId.toString())
	if (semester !== null && semester !== undefined)
		params.append("semester", semester.toString())
	if (semester1 !== null && semester1 !== undefined)
		params.append("semester1", semester1.toString())

	try {
		const response = await easyFetch(
			`http://localhost:8000/api/assignment/submissions/?${params.toString()}`,
			{ method: "GET" }
		)

		const data = await response.json()
		if (response.ok) {
			const uniqueStudents: { [id: number]: Student } = {}
			for (const submission of data.results) {
				const s = submission.student
				if (s && !uniqueStudents[s.id]) {
					uniqueStudents[s.id] = s
				}
			}
			return Object.values(uniqueStudents)
		} else {
			return {
				detail: data.detail ?? "Failed to fetch students from submissions.",
				status: response.status,
			}
		}
	} catch (err) {
		console.error(err)
		return {
			message: "Something went wrong fetching submitted students.",
		}
	}
}

export async function GetStudentsWithSimilarities(
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
): Promise<StudentResponse | APIError> {
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

		const url = `http://localhost:8000/api/cheating/submission-similarity-pairs/students-with-similarities/?${params.toString()}`

		const response = await easyFetch(url, { method: "GET" })
		const data = await response.json()

		if (response.ok) {
			return data as StudentResponse
		} else {
			return {
				detail:
					data.detail ?? "Failed to fetch students with similarity pairs.",
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
