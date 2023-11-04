from typing import List
from PyPDF2 import PdfReader
from pipeline.functions.VectorDB import vectordb
from pipeline.functions.FilesInFolder import get_files 
from pipeline.config.config import config
from pipeline.shared_content import status, logger
from tqdm import tqdm 

def load_docs():
    status.set_state(config.STATE_LOADING)

    logger.info(f"status is loading")
    logger.info("start loading files")

    files = get_files("", filter="pdf")
    for doc_path in tqdm(files):
        logger.info(f"start loading {doc_path}")
        reader = PdfReader("documents/"+doc_path)
        for i, page in enumerate(reader.pages):
            page_num = i + 1
            text = page.extract_text()
            vectordb.add_texts(
                    texts=[text],
                    # ids=["program_name"],
                    metadatas=[{"document": doc_path, "page": page_num}],
                    )
        logger.info(f"done loading {doc_path}")

    status.set_state(config.STATE_READY)
    logger.info(f"status is ready")
