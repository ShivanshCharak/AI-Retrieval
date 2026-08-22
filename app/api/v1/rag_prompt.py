RAG_PROMPT_TEMPLATE = """\
You are answering a user's question using retrieved knowledge-base context.

Instructions:
1. Answer the user's question directly.
2. Do not summarize the retrieved documents unless the user explicitly asks for a summary.
3. Use the retrieved context as supporting evidence, not as the task itself.
4. If the question is broad, organize your answer around 2-4 clear conceptual
   themes and only include themes with enough supporting evidence — don't try
   to touch every retrieved chunk.
5. Organize the answer around the user's topic, not around the order of the
   retrieved chunks below.
6. Do not refer to "the provided text", "the retrieved documents", or "the
   context" as meta-concepts. If a sub-topic isn't covered, say so briefly in
   your own words instead (e.g. "There isn't much detail here on X").
7. If the retrieved context does not contain enough information, say so
   rather than inventing details.
8. Each chunk below is labeled [n] (source, page). When a specific claim
   relies on one chunk, you may cite it inline as [n]. Don't cite for general
   framing sentences.
9. If the context covers multiple distinct senses of the topic (e.g. the same
   word used in unrelated subfields), address each sense under its own short
   heading rather than blending them together.

Then, generate a short conversation topic for the user's question.
The topic should:
- Be 3-7 words
- Clearly describe what the user is asking about
- Not be a sentence
- Not include quotes
- Not include punctuation at the end

User question:
{message}

Retrieved context:
{context}
"""


def build_rag_prompt(message: str, context_str: str) -> str:
    return RAG_PROMPT_TEMPLATE.format(message=message, context=context_str)
