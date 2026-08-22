from dataclasses import dataclass, field


@dataclass
class FormattedContext:
    context_str: str
    sources: list[dict] = field(default_factory=list)


def format_docs_for_prompt(docs) -> FormattedContext:
    """Turn retrieved docs into a clean, labeled context block for the LLM,
    and a de-duplicated list of source references for the frontend.

    This replaces the old one-liner that joined raw `page_content` only:

        context = "\n\n".join(doc.page_content for doc in docs)

    That threw away every bit of metadata (title, page_label, source file),
    so the model had nothing to organize or cite against, and the frontend
    had no way to show the user where an answer came from. Each chunk here
    is now labeled `[n] (Title, p.X)` so the LLM can cite `[n]` inline, and
    the same title/page pairs are returned as `sources` for the UI.
    """
    parts: list[str] = []
    sources: list[dict] = []
    seen: set[tuple] = set()

    for i, doc in enumerate(docs, 1):
        if hasattr(doc, "page_content"):
            content = doc.page_content
            metadata = getattr(doc, "metadata", {}) or {}
        else:
            content = doc.get("content", "")
            metadata = doc.get("metadata", {}) or {}

        content = (content or "").strip()
        if not content:
            continue

        title = metadata.get("title") or metadata.get("source") or "Unknown source"
        page = metadata.get("page_label") or metadata.get("page")
        label = f"{title}, p.{page}" if page else title

        parts.append(f"[{i}] ({label})\n{content}")

        dedup_key = (title, page)
        if dedup_key not in seen:
            seen.add(dedup_key)
            sources.append(
                {
                    "label": label,
                    "title": title,
                    "page": page,
                    "source": metadata.get("source"),
                }
            )

    return FormattedContext(context_str="\n\n".join(parts), sources=sources)
