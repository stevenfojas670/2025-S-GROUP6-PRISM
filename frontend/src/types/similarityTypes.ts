import { Submission } from "@/types/submissionTypes"

export interface SimilarityPair {
	id: number
	submission_id_1: Submission
	submission_id_2: Submission
	file_name: string
	match_id: number
	percentage: number
	assignment: number
}

export interface SimilarityPairResponse {
	count: number
	next: string | null
	previous: string | null
	current_page: number
	page_size: number
	results: SimilarityPair[]
}
