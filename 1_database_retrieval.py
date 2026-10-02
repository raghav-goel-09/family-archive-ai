import os
from typing import List, Dict
from dotenv import load_dotenv
from supabase import create_client, Client
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL and SUPABASE_KEY must be set in your .env file."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def create_database():
    """
    Supabase table creation is done once in Supabase SQL Editor.
    This function only checks that the table can be accessed.
    """
    try:
        supabase.table("archive_items").select("id").limit(1).execute()
    except Exception as error:
        raise RuntimeError(
            "Could not access the Supabase 'archive_items' table. "
            "Create the table using schema.sql and check your .env file."
        ) from error


def get_all_records() -> List[Dict]:
    response = supabase.table("archive_items").select("*").execute()
    return response.data or []


def retrieve_relevant_data(
    question: str,
    audience: str = "younger_members",
    top_k: int = 5
) -> List[Dict]:

    records = get_all_records()

    if audience == "younger_members":
        records = [
            r for r in records
            if r.get("sensitivity", "public") == "public"
        ]

    if not records:
        return []

    documents = [
        f"{r.get('item_type', '')} "
        f"{r.get('content', '')} "
        f"{r.get('source', '')} "
        f"{r.get('location') or ''} "
        f"{r.get('estimated_year') or ''} "
        f"{r.get('people') or ''}"
        for r in records
    ]

    vectorizer = TfidfVectorizer(stop_words="english")
    document_vectors = vectorizer.fit_transform(documents)
    question_vector = vectorizer.transform([question])
    similarities = cosine_similarity(
        question_vector,
        document_vectors
    )[0]

    ranked = similarities.argsort()[::-1]

    results = []

    for index in ranked[:top_k]:
        score = float(similarities[index])

        if score <= 0:
            continue

        record = records[index].copy()
        record["similarity_score"] = round(score, 4)
        results.append(record)

    return results


if __name__ == "__main__":
    create_database()

    question = input("Enter your question: ").strip()

    if not question:
        print("Please enter a question.")
    else:
        retrieved = retrieve_relevant_data(question)

        if not retrieved:
            print("No relevant public archive records were found.")
        else:
            print("\nRetrieved records:")

            for record in retrieved:
                print("-" * 60)
                print("Asset:", record.get("asset_id"))
                print("Type:", record.get("item_type"))
                print("Content:", record.get("content"))
                print("Source:", record.get("source"))
                print("Similarity:", record.get("similarity_score"))
