import { NextResponse } from "next/server"

export async function GET(request:Request){
     const cookie = request.headers.get("cookie")
    const res = await fetch("http://localhost:8000/api/v1/auth/me",{
        headers:{
            Cookie:cookie??""
        },
    })
    let response  = await res.json()
    
    return NextResponse.json(response,{status:res.status})
}