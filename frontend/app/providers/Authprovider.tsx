"use client"
import { AuthProvider } from "@/context/AuthContext";

export default function Authprovider({children}:{children:React.ReactNode}){
    return <AuthProvider>
        {children}
    </AuthProvider>
    
}