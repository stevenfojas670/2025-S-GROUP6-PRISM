"use client"
import {
	createContext,
	useContext,
	useState,
	useEffect,
	ReactNode,
} from "react"

interface CourseContextType {
	courseInstanceId: number | null
	setCourseInstanceId: (id: number | null) => void
}

const CourseContext = createContext<CourseContextType | undefined>(undefined)

export function CourseProvider({ children }: { children: ReactNode }) {
	const [courseInstanceId, setCourseInstanceIdState] = useState<number | null>(
		null
	)

	// Load from localStorage on mount
	useEffect(() => {
		const storedId = localStorage.getItem("course_instance_id")
		if (storedId) {
			setCourseInstanceIdState(Number(storedId))
		}
	}, [])

	// Sync to localStorage when value changes
	const setCourseInstanceId = (id: number | null) => {
		setCourseInstanceIdState(id)
		if (id !== null) {
			localStorage.setItem("course_instance_id", id.toString())
		} else {
			localStorage.removeItem("course_instance_id")
		}
	}

	return (
		<CourseContext.Provider value={{ courseInstanceId, setCourseInstanceId }}>
			{children}
		</CourseContext.Provider>
	)
}

export function useCourseContext() {
	const context = useContext(CourseContext)
	if (!context)
		throw new Error("useCourseContext must be used within CourseProvider")
	return context
}
