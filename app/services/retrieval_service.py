import numpy as np

from app.services.mongodb_service import MongoDBService


class RetrievalService:

    def __init__(self):
        self.mongo = MongoDBService()

    @staticmethod
    def cosine_similarity(vec1, vec2):
        """
        Compute cosine similarity between two vectors.
        """

        v1 = np.array(vec1, dtype=np.float32)
        v2 = np.array(vec2, dtype=np.float32)

        denominator = (
            np.linalg.norm(v1)
            * np.linalg.norm(v2)
        )

        if denominator == 0:
            return 0.0

        return float(
            np.dot(v1, v2) / denominator
        )

    def retrieve_candidates(
        self,
        job_embedding,
        top_n=50,
        filters=None,
    ):
        """
        Retrieve Top-N resumes based on embedding similarity.
        """

        resumes = self.mongo.get_all_resumes(
            filters
        )

        results = []

        for resume in resumes:

            if "embedding" not in resume:
                continue

            score = self.cosine_similarity(
                job_embedding,
                resume["embedding"],
            )

            resume["similarity_score"] = score

            results.append(resume)

        results.sort(
            key=lambda x: x["similarity_score"],
            reverse=True,
        )

        return results[:top_n]