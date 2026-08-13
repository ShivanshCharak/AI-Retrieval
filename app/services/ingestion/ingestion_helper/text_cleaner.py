import re
from langchain_core.documents import Document


def normalize_text(text: str) -> str:
    """
    Generic PDF text normalization.

    Does not assume a particular PDF format.
    """

    if not text:
        return ""

    # Normalize non-breaking spaces
    text = text.replace("\xa0", " ")

    # Normalize carriage returns
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Fix hyphenated words split across PDF lines:
    #
    # concur-
    # rency
    #
    # -> concurrency
    text = re.sub(
        r"(\w)-\n(\w)",
        r"\1\2",
        text,
    )

    # Replace multiple spaces/tabs
    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    # Remove spaces at beginning/end of lines
    text = re.sub(
        r" *\n *",
        "\n",
        text,
    )

    # Too many consecutive newlines
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    # Join lines that are obviously part of the same sentence.
    #
    # Example:
    #
    # Concurrency control allows transactions
    # to execute concurrently.
    #
    # ->
    #
    # Concurrency control allows transactions to execute concurrently.
    text = re.sub(
        r"(?<![.!?:;])\n(?=[a-z0-9])",
        " ",
        text,
    )

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
