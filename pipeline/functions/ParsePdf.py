from PyPDF2 import PdfReader
# from pipeline.functions.VectorDB import vectordb


# def parse_pdf(files):
#     for doc_path in files:

#         reader = PdfReader("documents/"+doc_path)
#         for i, page in enumerate(reader.pages):
#             page_num = i + 1
#             text = page.extract_text()
#             vectordb.add_texts(
#                     texts=[text],
#                     # ids=["program_name"],
#                     metadatas=[{"document": doc_path, "page": page_num}],
#                     )

def load_page_from_doc(doc_path, page) -> str:
    reader = PdfReader("documents"+doc_path)
    page = reader.pages[page-1]
    return page.extract_text()
