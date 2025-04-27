import { easyFetch } from "@/utils/fetchWrapper"
import {
	StudentEnrollments,
	StudentEnrollmentsResponse,
} from "@/types/studentTypes"
import { APIError } from "@/types/APIError"

export async function GetStudents(
	course_instance_id: number,
	no_paginate: boolean
): Promise<StudentEnrollmentsResponse | StudentEnrollments[] | APIError> {
	const queryParams = new URLSearchParams({
		course_instance: String(course_instance_id),
	})

	if (no_paginate) {
		queryParams.append("no_pagination", "true")
	}

	const response = await easyFetch(
		`http://localhost:8000/api/course/studentenrollments/?${queryParams}`,
		{ method: "GET" }
	)

	const data = await response.json()

	if (response.ok) {
		if (no_paginate) {
			return data as StudentEnrollments[]
		} else {
			return data as StudentEnrollmentsResponse
		}
	} else {
		return {
			detail: data.detail ?? "Failed to fetch students.",
			status: response.status,
		}
	}
}
