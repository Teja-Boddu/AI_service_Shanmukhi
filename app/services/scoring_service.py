from app.schemas.job_dto import JobDTO
from app.schemas.resume_dto import ResumeDTO


class ScoringService:

    @staticmethod
    def score_candidates(

        job: JobDTO,

        candidates: list,

    ):

        job_skills = {

            skill.lower()

            for skill in job.skills

        }

        results = []

        for candidate in candidates:

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

            skill_match = 0

            if len(job_skills) > 0:

                skill_match = (

                    len(matched)

                    / len(job_skills)

                )

            # ----------------------------
            # Normalize reranker score
            # ----------------------------

            rerank = candidate.get(
                "rerank_score",
                0,
            )

            rerank = max(
                0,
                min(
                    1,
                    (rerank + 5) / 10,
                ),
            )

            vector = candidate.get(
                "similarity_score",
                0,
            )

            # ----------------------------
            # Final weighted score
            # ----------------------------

            final_score = (

                0.45 * rerank

                +

                0.35 * vector

                +

                0.20 * skill_match

            )

            candidate["matched_skills"] = matched

            candidate["missing_skills"] = missing

            candidate["skill_match_percentage"] = round(

                skill_match * 100,

                2,

            )

            candidate["final_score"] = round(

                final_score,

                4,

            )

            results.append(candidate)

        results.sort(

            key=lambda x: x["final_score"],

            reverse=True,

        )

        return results