"use client";

import { usePathname } from "next/navigation";
import HeaderBar from "@/components/HeaderBar";
import React, { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext"
import { easyFetch } from "@/utils/fetchWrapper";

const routeTitles: Record<string, string> = {
  "/account/": "Account",
  "/alerts/": "Alerts",
  "/student_comparison/": "Student Comparison",
  // Add more paths and titles as needed
};

interface UserInfo {
	first_name: string
	last_name: string
}

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const hideHeader = pathname === "/login/";
  console.log(location.pathname);
  const { user } = useAuth();
  
  const [username, setUsername] = useState<UserInfo | null>(null);

  useEffect(() => {
    console.log("Current user:", user)
    if (!user?.professor_id) return
  
    const fetchUser = async () => {
      try {
        const res = await easyFetch(`http://localhost:8000/api/user/users`, {
      method: "GET"
    })
        if (!res.ok) throw new Error("Failed to fetch user info")
  
        const data = await res.json()
  
        const matchedUser = data.find((u: any) => u.id === user.professor_id)
  
        if (!matchedUser) throw new Error("User not found in response")
  
        console.log("Matched user:", matchedUser)
        setUsername({
          first_name: matchedUser.first_name,
          last_name: matchedUser.last_name
        })
      } catch (err) {
        console.error("Error loading user data:", err)
      }
    }
  
    fetchUser()
  }, [user?.professor_id])

  const getTitle = () => {
    if (pathname === "/dashboard/") return `Welcome, ${username?.first_name} ${username?.last_name}`;
    const match = Object.keys(routeTitles).find((key) => pathname.startsWith(key));
    return routeTitles[match || ""] || "Your App";
  };

  return (
    <>
      {!hideHeader && <HeaderBar title={getTitle()} />}
      <main>{children}</main>
    </>
  );
}
