from fastapi import APIRouter
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)
import pandas as pd

router = APIRouter()


def metrics(y_true, y_pred):
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(
            y_true,
            y_pred,
            average="weighted",
            zero_division=0,
        ),
        "recall": recall_score(
            y_true,
            y_pred,
            average="weighted",
            zero_division=0,
        ),
        "f1": f1_score(
            y_true,
            y_pred,
            average="weighted",
            zero_division=0,
        ),
    }


@router.get("/evaluation/classification")
async def classification_eval():

    router_df = pd.read_csv(
        "app/evaluation/evaluators/results/" "router_eval_2026-08-11_03-04-28.csv"
    )

    router_df = router_df.dropna(subset=["expected_route", "predicted_route"])

    router_metrics = metrics(
        router_df["expected_route"].astype(str),
        router_df["predicted_route"].astype(str),
    )

    # -------------------------
    # Retrieval Planner
    # -------------------------

    planner_df = pd.read_csv(
        "app/evaluation/evaluators/results/"
        "retrieval_planner_eval_2026-08-11_07-22-12.csv"
    )

    planner_metrics = {}

    for target in ["memory", "vector", "repo"]:

        y_true = planner_df[f"expected_use_{target}"].astype(bool)

        y_pred = planner_df[f"predicted_use_{target}"].astype(bool)

        planner_metrics[target] = metrics(
            y_true,
            y_pred,
        )

    return {
        "router": {
            "node": "Router",
            **router_metrics,
        },
        "retrieval_planner": {
            "node": "Retrieval Planner",
            "memory": planner_metrics["memory"],
            "vector": planner_metrics["vector"],
            "repo": planner_metrics["repo"],
        },
    }
