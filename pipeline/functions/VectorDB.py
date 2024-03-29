from langchain.vectorstores import Chroma
from pipeline.config.config import config
from langchain.embeddings import OpenAIEmbeddings
# from langchain.embeddings import SpacyEmbeddings
from dotenv import load_dotenv
import os


load_dotenv()
api_key = os.getenv("API_KEY", config.open_ai_key)
embedding = OpenAIEmbeddings(openai_api_key=api_key)

# embedding = SpacyEmbeddings()

vectordb = Chroma(
    collection_name="vectordb",
    embedding_function=embedding,
    persist_directory=f"db/vectordb",
)
