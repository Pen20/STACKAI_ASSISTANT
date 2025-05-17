# app/retrieval.py
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import faiss
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# ------- Keyword Search -------
def keyword_search(query: str, df: pd.DataFrame, columns: list):
    results = []
    for col in columns:
        if col in df.columns:
            mask = df[col].fillna("").str.contains(query, case=False, na=False)
            results.append(df[mask])
    return pd.concat(results).drop_duplicates() if results else pd.DataFrame()

# ------- Vector Search -------
class VectorRetriever:
    def __init__(self, texts: list, ids: list, model):
        self.texts = texts
        self.ids = ids
        self.model = model
        self.embeddings = self._embed_texts(texts)
        self.index = self._build_index(self.embeddings)

    def _embed_texts(self, texts):
        return np.array(self.model.encode(texts, show_progress_bar=False)).astype("float32")

    def _build_index(self, embeddings):
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        return index

    def search(self, query: str, top_k=5):
        query_vec = self.model.encode([query]).astype("float32")
        scores, idxs = self.index.search(query_vec, top_k)
        return [self.texts[i] for i in idxs[0]]

# ------- Graph Search with Neo4j -------
class GraphRetriever:
    def __init__(self, uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def search_nodes_by_keyword(self, keyword):
        query = (
            "MATCH (n) WHERE any(prop IN keys(n) WHERE toLower(toString(n[prop])) CONTAINS toLower($keyword)) "
            "RETURN n LIMIT 10"
        )
        with self.driver.session() as session:
            result = session.run(query, keyword=keyword)
            return [record["n"] for record in result]

    def search_paths_between_keywords(self, keyword1, keyword2):
        query = (
            "MATCH p=(a)-[*..3]-(b) "
            "WHERE any(prop IN keys(a) WHERE toLower(toString(a[prop])) CONTAINS toLower($k1)) "
            "AND any(prop IN keys(b) WHERE toLower(toString(b[prop])) CONTAINS toLower($k2)) "
            "RETURN p LIMIT 5"
        )
        with self.driver.session() as session:
            result = session.run(query, k1=keyword1, k2=keyword2)
            return [record["p"] for record in result]
