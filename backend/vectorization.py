
from docling.chunking import HybridChunker
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter


# Load env variables
import os
from dotenv import load_dotenv
load_dotenv()

from tqdm import tqdm


from backend.qdrant_Client import client


COLLECTION_NAME = os.getenv("COLLECTION_NAME")

converter = DocumentConverter()


# The :memory: mode is a Python imitation of Qdrant's APIs for prototyping and CI.
# For production deployments, use the Docker image: docker run -p 6333:6333 qdrant/qdrant
# client = QdrantClient(location="http://localhost:6333")

client.set_model("sentence-transformers/all-MiniLM-L6-v2")
client.set_sparse_model("Qdrant/bm25")


def convert_md(files):
    documents, metadatas = [], []
    chuncker = HybridChunker(max_tokens=300)
    
    
    for i in tqdm(range(len(files))):
        file_path = files[i]["path"]
        result = converter.convert(file_path)
        chuncks = chuncker.chunk(result.document)
        for chunk in chuncks:
            
            meta = chunk.meta.export_json_dict()

            metadata = {
                "heading": " > ".join(meta.get("headings", [])),
                "source": meta["origin"]["filename"],
                "course": files[i]["course"],
                "unit": files[i]["unit"],
                "note_type": files[i]["note_type"]
            }
            
            heading = " > ".join(meta.get("headings", []))
            embedding_text = f"{heading}\n\n{chunk.text}"
            
            documents.append(embedding_text)
            metadatas.append(metadata)
    print("Conversion completed.")
    return documents, metadatas


def addVectors(documents, metadatas):

    client.add(
        collection_name=COLLECTION_NAME,
        documents=documents,
        metadata=metadatas,
        batch_size=64
    )
    print("Vectors added successfully.")
    
    
def already_uploaded(filename):

    try:
        points, _ = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=10000,
            with_payload=True
        )

    except Exception:
        return False

    for point in points:

        if point.payload.get("source") == filename:
            return True

    return False
            
        

def initialize(files):
    
    for file in files:

        if already_uploaded(str(file["path"]).split("/")[-1]):
            print("Duplicate file")
        else:

            documents, metadatas = convert_md(files)
            addVectors(documents, metadatas)
    print("Initialization completed.")
    
    

    
    
        

    