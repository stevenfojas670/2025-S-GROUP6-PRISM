export interface AssignmentResponse {
	count: number
	next: string
	previous: string
	current_page: number
	page_size: number
	results: AssignmentItem[]
}

export interface AssignmentItem {
	id: number
	assignment_number: number
	title: string
	due_date: string | null
	lock_date: string | null
	pdf_filepath: string | null
	has_base_code: boolean | null
	moss_report_directory_path: string | null
	bulk_ai_directory_path: string | null
	language: string | null
	has_policy: boolean | null
	course_catalog: number | null
	semester: number | null
}

export type AssignmentCreatePayload = {
	course_catalog: number
	semester: number
	assignment_number: number
	title: string
	due_date: string
	lock_date: string
	pdf_filepath: string
	has_base_code: boolean
	moss_report_directory_path: string
	bulk_ai_directory_path: string
	language: string
	has_policy: boolean
	base_files: { filename: string; filepath: string }[]
	required_files: { filename: string }[]
	constraints: { type: string; value: string }[]
}
