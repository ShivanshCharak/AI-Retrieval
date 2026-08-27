from pathlib import Path
from datetime import datetime
import math

import pandas as pd

from app.services.retrieval_service import retrieve_context
from app.services.reranking.rerank import rerank_documents

# =========================================================
# CONFIG
# =========================================================

# Your 100-query golden dataset
CSV_PATH = Path(__file__).parent.parent / "datasets" / "retrieval_eval.csv"

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

OUTPUT_PATH = Path(__file__).parent / "results" / f"retrieval_eval_{timestamp}.csv"

# Evaluate these cutoffs
K_VALUES = [1, 3, 5, 10]

# Number of candidates retrieved BEFORE reranking
RETRIEVAL_K = 20

# Number of documents kept AFTER reranking
RERANK_K = 20


# =========================================================
# EXTRACT QDRANT DOCUMENT ID
# =========================================================


def get_document_id(doc):
    """
    Extract Qdrant point ID from:

    - LangChain Document
    - Qdrant objects
    - dict-based documents
    """

    # -----------------------------------------------------
    # LangChain Document
    # -----------------------------------------------------

    if hasattr(doc, "metadata"):

        metadata = doc.metadata or {}

        # Added by retrieve_context()
        if metadata.get("qdrant_id") is not None:
            return str(metadata["qdrant_id"])

        # Original ingestion ID
        if metadata.get("_id") is not None:
            return str(metadata["_id"])

        if metadata.get("id") is not None:
            return str(metadata["id"])

    # -----------------------------------------------------
    # Qdrant object
    # -----------------------------------------------------

    if hasattr(doc, "id"):

        doc_id = doc.id

        if doc_id is not None:
            return str(doc_id)

    # -----------------------------------------------------
    # Dictionary result
    # -----------------------------------------------------

    if isinstance(doc, dict):

        if doc.get("qdrant_id") is not None:
            return str(doc["qdrant_id"])

        if doc.get("id") is not None:
            return str(doc["id"])

        metadata = doc.get("metadata", {}) or {}

        if metadata.get("qdrant_id") is not None:
            return str(metadata["qdrant_id"])

        if metadata.get("_id") is not None:
            return str(metadata["_id"])

        if metadata.get("id") is not None:
            return str(metadata["id"])

    return None


# =========================================================
# RECIPROCAL RANK
# =========================================================


def reciprocal_rank(
    retrieved_ids,
    relevant_ids,
):
    """
    Reciprocal rank of the first relevant result.

    rank 1  -> 1.0
    rank 2  -> 0.5
    rank 3  -> 0.333
    not found -> 0
    """

    relevant_ids = set(relevant_ids)

    for rank, doc_id in enumerate(
        retrieved_ids,
        start=1,
    ):

        if doc_id in relevant_ids:

            return 1.0 / rank

    return 0.0


# =========================================================
# RECALL@K
# =========================================================


def recall_at_k(
    retrieved_ids,
    relevant_ids,
    k,
):

    retrieved = set(retrieved_ids[:k])

    relevant = set(relevant_ids)

    if not relevant:
        return 0.0

    return len(retrieved & relevant) / len(relevant)


# =========================================================
# HIT RATE@K
# =========================================================


def hit_rate_at_k(
    retrieved_ids,
    relevant_ids,
    k,
):

    retrieved = set(retrieved_ids[:k])

    relevant = set(relevant_ids)

    return 1.0 if retrieved & relevant else 0.0


# =========================================================
# NDCG@K
# =========================================================


def ndcg_at_k(
    retrieved_ids,
    relevant_ids,
    k,
):

    relevant = set(relevant_ids)

    dcg = 0.0

    for rank, doc_id in enumerate(
        retrieved_ids[:k],
        start=1,
    ):

        if doc_id in relevant:

            dcg += 1.0 / math.log2(rank + 1)

    # Ideal ranking
    ideal_relevant = min(
        len(relevant),
        k,
    )

    if ideal_relevant == 0:
        return 0.0

    idcg = sum(
        1.0 / math.log2(rank + 1)
        for rank in range(
            1,
            ideal_relevant + 1,
        )
    )

    return dcg / idcg


# =========================================================
# EVALUATE ONE QUERY
# =========================================================


def evaluate_row(row):

    query = str(row["query"])

    # -----------------------------------------------------
    # Golden chunk ID
    # -----------------------------------------------------

    expected_id = str(row["relevant_chunk_id"]).strip()

    try:

        # =================================================
        # STEP 1: RETRIEVAL
        # =================================================

        print("\n" + "=" * 80)

        print(f"QUERY {row.get('id', '')}: " f"{query}")

        print(f"Expected chunk: {expected_id}")

        print("Running retrieval...")

        result = retrieve_context(
            query=query,
            user_id=4,
            k=RETRIEVAL_K,
        )

        candidates = result or []

        print(f"Retrieved candidates: " f"{len(candidates)}")

        # =================================================
        # STEP 2: RERANK
        # =================================================

        print("Running reranker...")

        # IMPORTANT:
        # This is now sequential.
        # No asyncio.to_thread()
        # No semaphore.
        # No concurrent GPU inference.

        documents = rerank_documents(
            query=query,
            documents=candidates,
            top_k=RERANK_K,
        )

        # documents = reranked_documents or []

        print(f"After reranking: " f"{len(documents)}")

        # =================================================
        # STEP 3: EXTRACT IDS
        # =================================================

        retrieved_ids = []

        for doc in documents:

            doc_id = get_document_id(doc)

            if doc_id is not None:

                retrieved_ids.append(str(doc_id))

        # =================================================
        # STEP 4: FIND GOLD RANK
        # =================================================

        relevant_ids = [expected_id]

        rank = None

        for index, doc_id in enumerate(
            retrieved_ids,
            start=1,
        ):

            if doc_id == expected_id:

                rank = index

                break

        # =================================================
        # STEP 5: METRICS
        # =================================================

        recall = {}
        hit_rate = {}
        ndcg = {}

        for k in K_VALUES:

            recall[k] = recall_at_k(
                retrieved_ids,
                relevant_ids,
                k,
            )

            hit_rate[k] = hit_rate_at_k(
                retrieved_ids,
                relevant_ids,
                k,
            )

            ndcg[k] = ndcg_at_k(
                retrieved_ids,
                relevant_ids,
                k,
            )

        mrr = reciprocal_rank(
            retrieved_ids,
            relevant_ids,
        )

        passed = rank is not None

        # =================================================
        # DEBUG
        # =================================================

        print(f"{'PASSED' if passed else 'FAILED'}")

        print(f"Gold rank: {rank}")

        print(f"Top retrieved IDs:")

        for i, doc_id in enumerate(
            retrieved_ids[:10],
            start=1,
        ):

            marker = " <-- GOLD" if doc_id == expected_id else ""

            print(f"{i:>2}. {doc_id}{marker}")

        # =================================================
        # RETURN
        # =================================================

        return {
            "id": row.get(
                "id",
                "",
            ),
            "query": query,
            "topic": row.get(
                "topic_hint",
                "",
            ),
            "expected_id": expected_id,
            "expected_page": row.get(
                "relevant_page",
                "",
            ),
            "retrieved_ids": "|".join(retrieved_ids),
            "rank": rank,
            "recall@1": recall[1],
            "recall@3": recall[3],
            "recall@5": recall[5],
            "recall@10": recall[10],
            "hit_rate@1": hit_rate[1],
            "hit_rate@3": hit_rate[3],
            "hit_rate@5": hit_rate[5],
            "hit_rate@10": hit_rate[10],
            "ndcg@1": ndcg[1],
            "ndcg@3": ndcg[3],
            "ndcg@5": ndcg[5],
            "ndcg@10": ndcg[10],
            "mrr": mrr,
            "passed": passed,
            "error": "",
        }

    except Exception as e:

        print(
            f"FAILED "
            f"| query_id={row.get('id', '')} "
            f"| query={query} "
            f"| ERROR={e}"
        )

        return {
            "id": row.get(
                "id",
                "",
            ),
            "query": query,
            "topic": row.get(
                "topic_hint",
                "",
            ),
            "expected_id": expected_id,
            "expected_page": row.get(
                "relevant_page",
                "",
            ),
            "retrieved_ids": "",
            "rank": None,
            "recall@1": 0.0,
            "recall@3": 0.0,
            "recall@5": 0.0,
            "recall@10": 0.0,
            "hit_rate@1": 0.0,
            "hit_rate@3": 0.0,
            "hit_rate@5": 0.0,
            "hit_rate@10": 0.0,
            "ndcg@1": 0.0,
            "ndcg@3": 0.0,
            "ndcg@5": 0.0,
            "ndcg@10": 0.0,
            "mrr": 0.0,
            "passed": False,
            "error": str(e),
        }


# =========================================================
# MAIN
# =========================================================


def main():

    # =====================================================
    # LOAD DATASET
    # =====================================================

    df = pd.read_csv(CSV_PATH)

    print(f"Loaded golden dataset: " f"{CSV_PATH}")

    print(f"Evaluating " f"{len(df)} retrieval queries...")

    print(f"K values: {K_VALUES}")

    print(f"Retrieval K: {RETRIEVAL_K}")

    print(f"Rerank K: {RERANK_K}")

    # =====================================================
    # SANITY CHECKS
    # =====================================================

    required_columns = {
        "id",
        "query",
        "relevant_chunk_id",
    }

    missing = required_columns - set(df.columns)

    if missing:

        raise ValueError(f"Missing columns in " f"golden dataset: {missing}")

    print(f"Unique queries: " f"{df['query'].nunique()}")

    print(f"Unique gold chunks: " f"{df['relevant_chunk_id'].nunique()}")

    # =====================================================
    # SEQUENTIAL EVALUATION
    # =====================================================

    results = []

    total = len(df)

    for position, (_, row) in enumerate(
        df.iterrows(),
        start=1,
    ):

        print("\n" + "#" * 80)

        print(f"PROGRESS: " f"{position}/{total}")

        result = evaluate_row(row)

        results.append(result)

    # =====================================================
    # DATAFRAME
    # =====================================================

    results_df = pd.DataFrame(results)

    # =====================================================
    # SAVE RESULTS
    # =====================================================

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    results_df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    # =====================================================
    # AGGREGATE METRICS
    # =====================================================

    print("\n" + "=" * 30)

    print("Retrieval Evaluation")

    print("=" * 30)

    for k in K_VALUES:

        recall = results_df[f"recall@{k}"].mean()

        hit_rate = results_df[f"hit_rate@{k}"].mean()

        ndcg = results_df[f"ndcg@{k}"].mean()

        print(f"Recall@{k:<2}: " f"{recall:.4f} " f"({recall:.2%})")

        print(f"Hit Rate@{k:<2}: " f"{hit_rate:.4f} " f"({hit_rate:.2%})")

        print(f"nDCG@{k:<2}: " f"{ndcg:.4f}")

    # =====================================================
    # MRR
    # =====================================================

    mrr = results_df["mrr"].mean()

    print(f"\nMRR      : " f"{mrr:.4f}")

    # =====================================================
    # OVERALL
    # =====================================================

    hits = results_df["passed"].sum()

    total = len(results_df)

    overall_hit_rate = hits / total if total else 0.0

    print("\n" + "=" * 30)

    print("Overall")

    print(f"Queries  : " f"{total}")

    print(f"Hits     : " f"{hits}/{total}")

    print(f"Hit Rate : " f"{overall_hit_rate:.2%}")

    print(f"Saved to: " f"{OUTPUT_PATH}")

    print("=" * 30)


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()
