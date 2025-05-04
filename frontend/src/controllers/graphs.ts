import { easyFetch } from "@/utils/fetchWrapper"

export async function GetSimilarityPlot(id: number): Promise<string | null> {
	const response = await easyFetch(
		`http://localhost:8000/api/cheating/${id}/similarity-plot/`,
		{ method: "GET" }
	)

	if (!response.ok) return null

	const blob = await response.blob()
	return URL.createObjectURL(blob)
}

export async function GetDistributionPlot(id: number): Promise<string | null> {
	const response = await easyFetch(
		`http://localhost:8000/api/cheating/${id}/distribution-plot/`,
		{ method: "GET" }
	)

	if (!response.ok) return null

	const blob = await response.blob()
	return URL.createObjectURL(blob)
}

export async function GetSimilarityIntervalPlot(
	id: number
): Promise<string | null> {
	const response = await easyFetch(
		`http://localhost:8000/api/cheating/${id}/similarity-interval-plot/`,
		{ method: "GET" }
	)

	if (!response.ok) return null

	const blob = await response.blob()
	return URL.createObjectURL(blob)
}

export async function GetKmeansPlot(
	courseInstanceId: number,
	semesterId: number
): Promise<string | null> {
	const response = await easyFetch(
		`http://localhost:8000/api/cheating/kmeans-plot/${courseInstanceId}/${semesterId}/`,
		{ method: "GET" }
	)

	if (!response.ok) return null

	const blob = await response.blob()
	return URL.createObjectURL(blob)
}

export async function GetFullPipeline(
	courseInstanceId: number,
	semesterId: number
): Promise<string | null> {
	const response = await easyFetch(
		`http://localhost:8000/api/cheating/full-pipeline/${courseInstanceId}/${semesterId}/`,
		{ method: "GET" }
	)

	if (!response.ok) return null

	const blob = await response.blob()
	return URL.createObjectURL(blob)
}

export async function GetKmeansPairPlot(
	courseInstanceId: number,
	semesterId: number
): Promise<string | null> {
	const response = await easyFetch(
		`http://localhost:8000/api/cheating/kmeans-pairs-plot/${courseInstanceId}/${semesterId}/`,
		{ method: "GET" }
	)

	if (!response.ok) return null

	const blob = await response.blob()
	return URL.createObjectURL(blob)
}
