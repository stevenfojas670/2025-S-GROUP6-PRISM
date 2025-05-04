// Define the interface for a single semester
export interface Semester {
	id: number
	name: string
	year: number
	term: string
	session: string
}

// Define the interface for the API response
export interface SemesterResponse {
	count: number
	next: string | null
	previous: string | null
	current_page: number
	page_size: number
	results: Semester[]
}
