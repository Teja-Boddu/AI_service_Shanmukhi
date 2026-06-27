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

            RerankerService._tokenizer = AutoTokenizer.from_pretrained(
                "BAAI/bge-reranker-v2-m3"
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

    def rerank(
        self,
        job_text,
        resumes,
        top_k=5,
    ):

        scores = []

        with torch.no_grad():

            for resume in resumes:

                inputs = self.tokenizer(
                    job_text,
                    resume["raw_text"],
                    truncation=True,
                    padding=True,
                    max_length=512,
                    return_tensors="pt",
                )

                score = self.model(**inputs).logits.squeeze().item()

                resume["rerank_score"] = float(score)

                scores.append(resume)

        scores.sort(
            key=lambda x: x["rerank_score"],
            reverse=True,
        )

        return scores[:top_k]