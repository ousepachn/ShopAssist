from langchain.document_loaders import ReadTheDocsLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


class Preprocessing:
    def preprocess(self, sample_text):
        chunk_size = 300
        chunk_overlap = 50
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", " ", ""],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

        chunks = text_splitter.split_text(sample_text)
        metadata = [{"source": "Not right now"} for i in chunks]

        return [chunks, metadata]
