export default async function getChatHistory() {
  try {
    const response = await fetch(
      "http://localhost:8000/api/v1/conversations",
      {
        credentials: "include",
        method: "GET",
      }
    );

    const parsedData = await response.json();

    return parsedData.result;
  } catch (error) {
    console.error("Something went wrong", error);
    return [];
  }
}