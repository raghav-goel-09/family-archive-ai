import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def generate_answer(question: str, processed_context: str) -> str:

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return "ERROR: OPENAI_API_KEY is not set in your .env file."

    client = OpenAI(api_key=api_key)

    model = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

    instructions = """You are a Family Archive Story Assistant.
Answer using ONLY the supplied archive context.

Rules:
1. Do not invent family facts.
2. If the archive contains conflicting memories, do not choose a winner.
3. Explain different accounts and name their sources.
4. If information is uncertain, say it is uncertain.
5. Keep the answer warm, simple, and easy for younger family members to understand.
6. Mention the source for important factual details.
7. Do not reveal records that are not in the supplied context."""

    user_input = (
        f"USER QUESTION:\n{question}\n\n"
        f"RETRIEVED AND PROCESSED ARCHIVE CONTEXT:\n"
        f"{processed_context}\n\n"
        "Answer the question using the archive context above."
    )

    try:
        response = client.responses.create(
            model=model,
            instructions=instructions,
            input=user_input
        )

        return response.output_text

    except Exception as error:
        return f"GenAI error: {error}"


if __name__ == "__main__":
    question = input("Question: ").strip()
    context = input("Test context: ").strip()
    print("\n" + generate_answer(question, context))
