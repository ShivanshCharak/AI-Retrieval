"use client"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"


import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { useState } from "react"
import Link from "next/link"
import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import Loader from "./loader"
import {toast} from "sonner"

export function SignupForm({ ...props }: React.ComponentProps<typeof Card>) {
  const [email, setEmail] = useState<string>("")
  const [name, setName] = useState<string>("")
  const [password, setPassword]  = useState<string>("")
  const [confirmPassword, setConfirmPassword] = useState<string>("")
  const route = useRouter()




  async function handleSubmit(e:React.SubmitEvent<HTMLFormElement>){
    e.preventDefault()
    const payload ={
      email,
      name,
      password
    }
    await fetch("/api/auth/signup",{
      method:"POST",
      headers:{
        "Content-type":"application/json"
      },
      body: JSON.stringify(payload) 
    }).then(async (res)=>{
      let response = await res.json()
      if (response.status_code===200){
        route.push("/login")
        toast.success("Account created")
      }else{
        toast.error("Something went wrong")
      }
    
    })
  }

  return (
    <Card {...props}>
      <CardHeader>
        <CardTitle>Create an account</CardTitle>
        <CardDescription>
          Enter your information below to create your account
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={(e)=>handleSubmit(e)}>
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="name">Full Name</FieldLabel>
              <Input id="name" type="text" placeholder="John Doe" value={name} onChange={(e)=> setName(e.target.value)} required />
            </Field>
            <Field>
              <FieldLabel htmlFor="email">Email</FieldLabel>
              <Input
                id="email"
                type="email"
                placeholder="m@example.com"
                value={email}
                onChange={(e)=>setEmail(e.target.value) }
                required
              />
              <FieldDescription>
                We&apos;ll use this to contact you. We will not share your email
                with anyone else.
              </FieldDescription>
            </Field>
            <Field>
              <FieldLabel htmlFor="password">Password</FieldLabel>
              <Input id="password" value={password} onChange={(e)=> setPassword(e.target.value)} type="password" required />
              <FieldDescription>
                Must be at least 8 characters long.
              </FieldDescription>
            </Field>
            <Field>
              <FieldLabel htmlFor="confirm-password">
                Confirm Password
              </FieldLabel>
              <Input id="confirm-password" type="password" required value={confirmPassword} onChange={(e)=> setConfirmPassword(e.target.value)} />
              <FieldDescription>Please confirm your password.</FieldDescription>
            </Field>
            <FieldGroup>
              <Field>
                <Button type="submit">Create Account</Button>
                <Button variant="outline" type="button">
                  Sign up with Google
                </Button>
                <FieldDescription className="px-6 text-center">
                  Already have an account? <Link href="/login">Sign in</Link>
                </FieldDescription>
              </Field>
            </FieldGroup>
          </FieldGroup>
        </form>
      </CardContent>
    </Card>
  )
}
