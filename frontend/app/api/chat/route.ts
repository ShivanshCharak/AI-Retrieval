import { NextResponse } from "next/server";

export async function POST(req: Request) {
  const formData = await req.formData();
  const cookie =  req.headers.get("cookie")


  const backendForm = new FormData();

  const message = formData.get("message");
  const model = formData.get("model");
  const file = formData.get("file");
  const deepSearch = formData.get("deep_search")

  if (message) backendForm.append("message", message);
  if (model) backendForm.append("model", model);
  if (deepSearch) backendForm.append("deep_search", deepSearch)

  if (file && file instanceof File) {
    backendForm.append("file", file);
  }



  const res = await fetch("http://localhost:8000/api/v1/chat", {
    headers:{
      Cookie:cookie??""
    },
  method: "POST",
  body: backendForm,
});

return new Response(res.body, {
  headers: {
    "Content-Type": "text/event-stream",
    "Cache-Control":"no-cache",
    "Connection":"keep-alive"
  },
})}