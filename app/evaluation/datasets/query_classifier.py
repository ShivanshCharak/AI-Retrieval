import pandas as pd
from pathlib import Path
from app.services.query_translation.query_classifier import classify_query

CSV_PATH = Path(__file__).parent / "query_classifier_eval.csv"

df = pd.read_csv(CSV_PATH)

for _, row in df.iterrows():
    query = row["query"]
    expected = row["expected_category"]

    predicted = classify_query(query)

    print(query, expected, predicted)
