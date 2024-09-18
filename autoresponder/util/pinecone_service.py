# utility_service.py or in utils.py within your app directory
from typing import List

from pinecone import Pinecone
from django.conf import settings

import gpt_model_manger


class PineconeService:

    @staticmethod
    def similarity_search(query_text, namespace="analog-catalog", top_k=5) -> List:
        try:
            pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            index = pc.Index("pvs-index")

            query_embedding = gpt_model_manger.GPTModelManager().EMBEDDINGS_GPT.embed_query(query_text)
            query_embedding = list(query_embedding)
            response = index.query(vector=query_embedding, top_k=top_k, namespace=namespace, include_metadata=True)
            return response['matches']
        except Exception:
            return []

