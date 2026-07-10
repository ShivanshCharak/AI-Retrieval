import { NextResponse } from "next/server"

export async function POST(req:Request){
    const body  = await req.json()
     const response = await fetch("http://localhost:8000/api/v1/auth/signin",{
        headers:{
            "Content-Type":"application/json"
        },
        body: JSON.stringify(body),
        method:"POST"
     })
     const data = await response.json()
     const nextresponse = NextResponse.json(data,{status:response.status})
     const setcookies = response.headers.get("set-cookie")
     if (setcookies){
        nextresponse.headers.set("set-cookie", setcookies)
     }
     return nextresponse
}
