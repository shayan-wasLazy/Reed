from ollama import chat
from backend.qdrant_Client import client

import os
from dotenv import load_dotenv
load_dotenv()

COLLECTION_NAME = os.getenv("COLLECTION_NAME")


def ask_rag(query_text: str):
    points = client.query(
        collection_name=COLLECTION_NAME,
        query_text=query_text,
        limit=5,
    )
    
    context = "\n\n".join(
        point.document
        for point in points
    )
    promt = f"""You are a study assistant.

Answer ONLY using the provided context.

If the answer is not present in the context,
reply exactly:

"I could not find that in the uploaded notes."
Context: {context} \n\n Question: {query_text} \n\n Answer:"""
    response = chat(
        model="qwen3:4b",
        messages=[
            {
                "role": "user",
                "content": promt
            }
        ]
    )

    return(response.message.content)