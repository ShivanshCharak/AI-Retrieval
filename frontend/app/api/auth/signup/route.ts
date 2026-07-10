import { NextResponse } from "next/server";

export async function POST(req:Request){
    const body = await req.json()

    const response = await fetch("http://localhost:8000/api/v1/auth/signup",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify(body)
    })
    const data = await response.json()
    return NextResponse.json(data)
}