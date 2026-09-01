def reciprocal_rank_fusion(dense_results, sparse_results, k=20):
    scores = {}
    results = {}

    for rank, point in enumerate(dense_results, start=1):
        point_id = str(point.id)

        scores[point_id] = scores.get(point_id, 0) + 1 / (k + rank)
        results[point_id] = point

    for rank, point in enumerate(sparse_results, start=1):
        point_id = str(point.id)

        scores[point_id] = scores.get(point_id, 0) + 1 / (k + rank)
        results[point_id] = point

    ranked_ids = sorted(scores, key=scores.get, reverse=True)

    return [results[point_id] for point_id in ranked_ids]
