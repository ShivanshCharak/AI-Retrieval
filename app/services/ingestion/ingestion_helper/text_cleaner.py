import re

from langchain_core.documents import Document
from typing import List

import re


def normalize_text(text: str) -> str:
    """
    Normalize PDF-extracted text for RAG.

    Converts PDF formatting whitespace into normal spaces
    while preserving paragraph breaks where there are multiple
    consecutive newlines.
    """

    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Non-breaking spaces -> normal spaces
    text = text.replace("\xa0", " ")

    # Literal escaped hyphens -> normal hyphens
    text = text.replace("\\-", "-")

    # Tabs -> spaces
    text = text.replace("\t", " ")

    # Fix words split across a PDF line:
    #
    # distributed
    # systems
    #
    # -> distributed systems
    #
    # But:
    #
    # partition-
    # tolerant
    #
    # -> partition-tolerant
    text = re.sub(
        r"([A-Za-z])-\n([A-Za-z])",
        r"\1-\2",
        text,
    )

    # Convert remaining single newlines into spaces.
    #
    # "Proceedings of the sixth
    # annual ACM Symposium"
    #
    # -> "Proceedings of the sixth annual ACM Symposium"
    text = re.sub(r"\n+", " ", text)

    # Remove spaces before punctuation
    #
    # "Machinery ."
    # -> "Machinery."
    text = re.sub(
        r"\s+([,.;:!?])",
        r"\1",
        text,
    )

    # Remove spaces around parentheses
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)

    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def clean_documents(
    documents: list[Document],
) -> list[Document]:

    cleaned_documents = []

    for document in documents:
        cleaned_text = normalize_text(document.page_content)

        if not cleaned_text:
            continue

        cleaned_documents.append(
            Document(
                page_content=cleaned_text,
                metadata=document.metadata.copy(),
            )
        )

    return cleaned_documents


def merge_document(documents: List[Document]) -> Document:

    merged_text_parts = []
    offset = 0
    page_offsets = []

    for doc in documents:
        page_offsets.append((offset, doc.metadata.get("page_label")))

        merged_text_parts.append(doc.page_content)

        offset += len(doc.page_content) + 1

    merged_text = "\n".join(merged_text_parts)

    base_metadata = documents[0].metadata.copy() if documents else {}

    base_metadata.pop("page", None)
    base_metadata.pop("page_label", None)

    base_metadata["page_offsets"] = page_offsets

    return Document(
        page_content=merged_text,
        metadata=base_metadata,
    )
