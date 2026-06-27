from app.schemas.job_dto import JobDTO

from app.services.llm_service import LLMService
from app.services.embedding_service import EmbeddingService
from app.services.mongodb_service import MongoDBService
from app.services.retrieval_service import RetrievalService
from app.services.reranker_service import RerankerService


class JobService:

    def __init__(self):

        self.llm = LLMService()

        self.embedding = EmbeddingService()

        self.mongo = MongoDBService()

        self.retrieval = RetrievalService()

        self.reranker = RerankerService()

    def process_job(

        self,

        job_description: str,

        top_k: int = 5,

        filters: dict | None = None,

    ):

        # -----------------------------------
        # Step 1 Extract Structured Job
        # -----------------------------------

        parsed = self.llm.call_llm(

            "job_prompt.txt",

            job_description,

        )

        job = JobDTO(**parsed)

        # -----------------------------------
        # Step 2 Generate Job Embedding
        # -----------------------------------

        job_embedding = self.embedding.generate_job_embedding(
            job
        )

        # -----------------------------------
        # Step 3 Store Job
        # -----------------------------------

        job_id = self.mongo.save_job(
            job,
            job_embedding,
        )

        # -----------------------------------
        # Step 4 Retrieve Candidates
        # -----------------------------------

        retrieved = self.retrieval.retrieve_candidates(

            job_embedding,

            top_n=50,

            filters=filters,

        )

        # -----------------------------------
        # Step 5 Rerank
        # -----------------------------------

        ranked = self.reranker.rerank(

            job_description,

            retrieved,

            top_k,

        )

        # -----------------------------------
        # Step 6 Build Response
        # -----------------------------------

        candidates = []

        rank = 1

        for resume in ranked:

            candidates.append({

                "rank": rank,

                "candidate_name": resume.get("candidate_name"),

                "email": resume.get("email"),

                "skills": resume.get("skills"),

                "similarity_score": round(

                    resume["similarity_score"],

                    4,

                ),

                "rerank_score": round(

                    resume["rerank_score"],

                    4,

                ),

            })

            rank += 1

        return {

            "message": "Matching Completed",

            "job_id": job_id,

            "job": job.model_dump(),

            "total_candidates": len(retrieved),

            "top_k": top_k,

            "matches": candidates,

        }