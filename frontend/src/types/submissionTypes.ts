import { AssignmentItem } from "@/types/assignmentTypes"
import { Student } from "@/types/studentTypes"

export interface Submission {
	id: number
	student: Student
	assignment: AssignmentItem
	grade: string
	created_at: string
	flagged: boolean
	file_path: string
	course_instance: number
}

export interface SubmissionResponse {
	count: number
	next: string | null
	previous: string | null
	current_page: number
	page_size: number
	results: Submission[]
}
