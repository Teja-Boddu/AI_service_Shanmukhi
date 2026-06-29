from app.schemas.job_dto import JobDTO


class ScoringService:

    @staticmethod
    def score_candidates(
        job: JobDTO,
        candidates: list,
    ):

        if not candidates:
            return []

        # ------------------------------------------
        # Normalize Reranker Scores (0-100)
        # ------------------------------------------

        rerank_scores = [
            candidate.get("rerank_score", 0)
            for candidate in candidates
        ]

        min_rerank = min(rerank_scores)
        max_rerank = max(rerank_scores)

        job_skills = {
            skill.lower()
            for skill in job.skills
        }

        results = []

        for candidate in candidates:

            # ------------------------------------------
            # Skill Matching
            # ------------------------------------------

            resume_skills = {
                skill.lower()
                for skill in candidate.get(
                    "skills",
                    []
                )
            }

            matched = sorted(
                list(
                    job_skills.intersection(
                        resume_skills
                    )
                )
            )

            missing = sorted(
                list(
                    job_skills.difference(
                        resume_skills
                    )
                )
            )

            if job_skills:

                skill_match = (
                    len(matched)
                    / len(job_skills)
                ) * 100

            else:

                skill_match = 0

            # ------------------------------------------
            # Normalize MongoDB Vector Score
            # ------------------------------------------

            similarity = (
                candidate.get(
                    "similarity_score",
                    0,
                )
                * 100
            )

            # ------------------------------------------
            # Normalize Reranker Score
            # ------------------------------------------

            rerank = candidate.get(
                "rerank_score",
                0,
            )

            if max_rerank != min_rerank:

                rerank = (
                    (rerank - min_rerank)
                    /
                    (max_rerank - min_rerank)
                ) * 100

            else:

                rerank = 100

            # ------------------------------------------
            # Final Match Score
            # ------------------------------------------

            final_score = (

                0.40 * similarity

                +

                0.40 * rerank

                +

                0.20 * skill_match

            )

            # ------------------------------------------
            # Save Results
            # ------------------------------------------

            candidate["matched_skills"] = matched

            candidate["missing_skills"] = missing

            candidate["skill_match_percentage"] = round(
                skill_match,
                2,
            )

            candidate["similarity_score"] = round(
                similarity,
                2,
            )

            candidate["rerank_score"] = round(
                rerank,
                2,
            )

            candidate["final_score"] = round(
                final_score,
                2,
            )

            results.append(candidate)

        results.sort(
            key=lambda x: x["final_score"],
            reverse=True,
        )

        return results