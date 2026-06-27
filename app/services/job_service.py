from app.schemas.job_dto import JobDTO

from app.services.llm_service import LLMService
from app.services.embedding_service import EmbeddingService
from app.services.mongodb_service import MongoDBService
from app.services.retrieval_service import RetrievalService
from app.services.reranker_service import RerankerService
from app.services.scoring_service import ScoringService


class JobService:

    def __init__(self):

        self.llm = LLMService()

        self.embedding_service = EmbeddingService()

        self.mongo = MongoDBService()

        self.retrieval = RetrievalService()

        self.reranker = RerankerService()

        self.scorer = ScoringService()

    # ---------------------------------------------------

    def match_job(

        self,

        job_description: str,

        top_k: int = 5,

        filters: dict | None = None,

    ):

        # -----------------------------------
        # Extract Structured Job
        # -----------------------------------

        parsed = self.llm.call_llm(

            "job_prompt.txt",

            job_description,

        )

        job = JobDTO(

            **parsed,

        )

        # -----------------------------------
        # Job Embedding
        # -----------------------------------

        job_embedding = (

            self.embedding_service.generate_job_embedding(

                job

            )

        )

        # -----------------------------------
        # Load resumes
        # -----------------------------------

        resumes = self.mongo.get_all_resumes()

        # -----------------------------------
        # Retrieve Top 50
        # -----------------------------------

        retrieved = (

            self.retrieval.retrieve_candidates(

                job_embedding=job_embedding,

                resumes=resumes,

                top_n=50,

                filters=filters,

            )

        )

        # -----------------------------------
        # Rerank Top 50
        # -----------------------------------

        reranked = (

            self.reranker.rerank(

                job_description,

                retrieved,

                top_k=50,

            )

        )

        # -----------------------------------
        # Hybrid Scoring
        # -----------------------------------

        scored = (

            self.scorer.score_candidates(

                job,

                reranked,

            )

        )
        for rank, candidate in enumerate(scored, start=1):

            candidate["rank"] = rank

        matches = []

        for candidate in scored[:top_k]:

            matches.append({

                "rank": candidate["rank"],

                "candidate_name": candidate.get("candidate_name"),

                "email": candidate.get("email"),

                "phone": candidate.get("phone"),

                "location": candidate.get("location"),

                "experience": candidate.get("total_experience"),

                "skills": candidate.get("skills"),

                "similarity_score": candidate.get("similarity_score"),

                "rerank_score": candidate.get("rerank_score"),

                "final_score": candidate.get("final_score"),

                "skill_match_percentage": candidate.get("skill_match_percentage"),

                "matched_skills": candidate.get("matched_skills"),

                "missing_skills": candidate.get("missing_skills"),

            })

        # -----------------------------------
        # Return Top K
        # -----------------------------------
        return {

            "job": job,

            "total_candidates": len(resumes),

            "retrieved": len(retrieved),

            "returned": min(

                top_k,

                len(scored),

            ),

            "matches": matches,

        }