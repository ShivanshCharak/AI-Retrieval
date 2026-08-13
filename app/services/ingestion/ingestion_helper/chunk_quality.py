import re
from collections import Counter


def count_urls(text: str) -> int:
    return len(
        re.findall(
            r"https?://\S+",
            text,
            re.IGNORECASE,
        )
    )


def count_reference_patterns(text: str) -> int:

    patterns = [
        r"\[[A-Z]{2,}\d{2,}\]",
        r"\bProceedings of\b",
        r"\bTechnical Report\b",
        r"\bInternational Journal\b",
        r"\bACM Computing Surveys\b",
        r"\bIEEE Transactions\b",
        r"\bReferences\b",
        r"\bBibliography\b",
    ]

    count = 0

    for pattern in patterns:
        if re.search(
            pattern,
            text,
            re.IGNORECASE,
        ):
            count += 1

    return count


def alphabetic_ratio(text: str) -> float:

    if not text:
        return 0.0

    alphabetic = sum(character.isalpha() for character in text)

    return alphabetic / len(text)


def is_low_quality_chunk(text: str) -> bool:

    text = text.strip()

    # Almost empty
    if len(text) < 100:
        return True

    # Mostly symbols/numbers
    if alphabetic_ratio(text) < 0.35:
        return True

    # Excessive URLs
    if count_urls(text) >= 4:
        return True

    # Strong reference/bibliography signal
    if count_reference_patterns(text) >= 3:
        return True

    return False


def filter_chunks(chunks):

    valid_chunks = []
    rejected_chunks = []

    for chunk in chunks:

        if is_low_quality_chunk(chunk.page_content):
            rejected_chunks.append(chunk)
        else:
            valid_chunks.append(chunk)

    return valid_chunks, rejected_chunks
