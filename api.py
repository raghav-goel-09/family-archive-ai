from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Family Archive AI API")

# Allows the Lovable frontend to call this Python backend.
# During development this is intentionally open.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_module(filename: str, module_name: str):
    path = BASE_DIR / filename
    spec = spec_from_file_location(module_name, path)

    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {filename}")

    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {"message": "Family Archive AI backend is running."}


@app.post("/ask")
def ask_archive(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        return {
            "answer": "Please enter a question.",
            "conflicts": [],
            "records_found": 0
        }

    retrieval = load_module(
        "1_database_retrieval.py",
        "database_retrieval_api"
    )

    processor = load_module(
        "2_process_data.py",
        "process_data_api"
    )

    genai = load_module(
        "3_genai.py",
        "genai_api"
    )

    # 1. Get records from Supabase
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

    # 2. Process records / detect conflicts
    processed = processor.process_retrieved_data(
        records,
        audience="younger_members"
    )

    # 3. Send RAG context to GenAI
    answer = genai.generate_answer(
        question,
        processed["context"]
    )

    return {
        "answer": answer,
        "conflicts": processed["conflicts"],
        "records_found": len(records)
    }
