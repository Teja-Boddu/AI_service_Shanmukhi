import numpy as np


class RetrievalService:

    @staticmethod
    def cosine_similarity(

        query_embedding,

        candidate_embedding,

    ):

        query = np.array(query_embedding)

        candidate = np.array(candidate_embedding)

        return float(

            np.dot(query, candidate)

            /

            (

                np.linalg.norm(query)

                *

                np.linalg.norm(candidate)

            )

        )

    # ---------------------------------------------

    def retrieve_candidates(

        self,

        job_embedding,

        resumes,

        top_n=50,

        filters=None,

    ):

        retrieved = []

        for resume in resumes:

            # ------------------------
            # Apply Filters
            # ------------------------

            if filters:

                location = filters.get(
                    "location"
                )

                if location:

                    if (

                        resume.get(
                            "location",
                            "",
                        ).lower()

                        !=

                        location.lower()

                    ):

                        continue

            similarity = self.cosine_similarity(

                job_embedding,

                resume["embedding"],

            )

            resume["similarity_score"] = round(

                similarity,

                4,

            )

            retrieved.append(

                resume

            )

        retrieved.sort(

            key=lambda x: x["similarity_score"],

            reverse=True,

        )

        return retrieved[:top_n]