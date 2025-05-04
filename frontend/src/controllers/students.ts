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
	course: number | null,
	assignmentId: number | null,
	semester: number | null,
	semester1: number | null
): Promise<Student[] | APIError> {
	const params = new URLSearchParams()
	if (course) params.append("course", course.toString())
	if (assignmentId) params.append("asid", assignmentId.toString())
	if (semester) params.append("semester", semester.toString())
	if (semester1) params.append("semester1", semester1.toString())

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
