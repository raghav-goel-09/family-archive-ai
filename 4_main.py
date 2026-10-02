from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def load_module(filename: str, module_name: str):
    path = BASE_DIR / filename

    spec = spec_from_file_location(module_name, path)

    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {filename}")

    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def run_archive_question(question: str):
    retrieval = load_module(
        "1_database_retrieval.py",
        "database_retrieval"
    )

    processor = load_module(
        "2_process_data.py",
        "process_data"
    )

    genai = load_module(
        "3_genai.py",
        "genai_module"
    )

    retrieval.create_database()

    records = retrieval.retrieve_relevant_data(
        question,
        audience="younger_members",
        top_k=5
    )

    if not records:
        return {
            "answer": "No relevant public archive records were found.",
            "conflicts": [],
            "records_found": 0
        }

    processed = processor.process_retrieved_data(
        records,
        audience="younger_members"
    )

    answer = genai.generate_answer(
        question,
        processed["context"]
    )

    return {
        "answer": answer,
        "conflicts": processed["conflicts"],
        "records_found": len(records)
    }


def main():

    print("=" * 60)
    print("       FAMILY ARCHIVE - AI STORY ASSISTANT")
    print("=" * 60)

    question = input(
        "\nAsk a question about the family archive:\n> "
    ).strip()

    if not question:
        print("Please enter a question.")
        return

    result = run_archive_question(question)

    print("\nFINAL FAMILY ARCHIVE ANSWER")
    print("=" * 60)
    print(result["answer"])
    print("=" * 60)


if __name__ == "__main__":
    main()
