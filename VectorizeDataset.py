from langchain.document_loaders import ReadTheDocsLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import csv


class Preprocessing:
    def __init__(self):
        self.meta_data = self.read_csv()

    def preprocess(self, sample_text, PATH):
        chunk_size = 200
        chunk_overlap = 50
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", " ", ""],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

        chunks = text_splitter.split_text(sample_text)
        metadata = self.meta_data[PATH]

        return [chunks, metadata]

    def read_csv(self):
        with open('hydrationceo-posts.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            meta_data = []
            for row in csv_reader:
                meta_data.append(row)

        return {i[6].split("\\")[1]: i for i in meta_data[1:]}
