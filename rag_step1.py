from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

text = Path("knowledge/greentech.txt").read_text(encoding="utf-8")

doc = Document(page_content=text, metadata={"source" : "greentech.txt"})

splitter = RecursiveCharacterTextSplitter(chunk_size=120, chunk_overlap=30)

chunks = splitter.split_documents([doc])

print("Number of chunks: ", len(chunks))

for i, chunk in enumerate(chunks, 1):
    print(f"--- chunk {i} ({len(chunk.page_content)} chars) ---")
    print(chunk.page_content)