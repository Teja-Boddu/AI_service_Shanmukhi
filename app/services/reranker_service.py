from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)

import torch

from app.core.logging import logger


class RerankerService:

    _tokenizer = None
    _model = None

    def __init__(self):

        if RerankerService._model is None:

            logger.info("Loading BGE Reranker...")

            RerankerService._tokenizer = (
                AutoTokenizer.from_pretrained(
                    "BAAI/bge-reranker-v2-m3"
                )
            )

            RerankerService._model = (
                AutoModelForSequenceClassification.from_pretrained(
                    "BAAI/bge-reranker-v2-m3"
                )
            )

            RerankerService._model.eval()

            logger.info("BGE Reranker Loaded.")

        self.tokenizer = RerankerService._tokenizer
        self.model = RerankerService._model

    # ---------------------------------------------------

    def build_resume_text(
        self,
        resume,
    ):

        text = []

        text.append(
            f"Candidate: {resume.get('candidate_name','')}"
        )

        text.append(
            f"Experience: {resume.get('total_experience','')}"
        )

        text.append(
            "Skills:"
        )

        text.extend(
            resume.get(
                "skills",
                []
            )
        )

        text.append(
            "Education:"
        )

        for edu in resume.get(
            "education",
            []
        ):

            text.append(

                f"{edu.get('degree','')} "

                f"{edu.get('specialization','')} "

                f"{edu.get('institution','')}"

            )

        text.append(
            "Projects:"
        )

        for project in resume.get(
            "projects",
            []
        ):

            text.append(

                project.get(
                    "title",
                    ""
                )

            )

            text.append(

                project.get(
                    "description",
                    ""
                )

            )

        text.append(
            "Certifications:"
        )

        for cert in resume.get(
            "certifications",
            []
        ):

            text.append(

                cert.get(
                    "name",
                    ""
                )

            )

        return "\n".join(text)

    # ---------------------------------------------------

    def rerank(

        self,

        job_description,

        resumes,

        top_k=5,

    ):

        ranked = []

        with torch.no_grad():

            for resume in resumes:

                resume_text = self.build_resume_text(
                    resume
                )

                inputs = self.tokenizer(

                    job_description,

                    resume_text,

                    truncation=True,

                    padding=True,

                    max_length=512,

                    return_tensors="pt",

                )

                score = (

                    self.model(
                        **inputs
                    )

                    .logits

                    .squeeze()

                    .item()

                )

                resume["rerank_score"] = round(
                    score,
                    4,
                )

                ranked.append(
                    resume
                )

        ranked.sort(

            key=lambda x: x["rerank_score"],

            reverse=True,

        )

        return ranked[:top_k]