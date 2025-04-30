export interface CourseCatalog {
	id: number
	name: string
	subject: string
	catalog_number: number
	course_title: string
	course_level: string
}

export interface Course {
	id: number
	course_catalog: CourseCatalog
	section_number: number
	canvas_course_id: number
	semester: number
	professor: number
	teaching_assistant: number | null
}

export interface CourseResponse {
	count: number
	next: string | null
	previous: string | null
	results: Course[]
}
