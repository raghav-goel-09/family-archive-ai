FAMILY ARCHIVE AI - BACKEND

1. Create a Supabase project.
2. Open Supabase SQL Editor.
3. Paste and run schema.sql.
4. Copy .env.example to .env.
5. Put your real Supabase and OpenAI keys in .env.
6. Open a terminal in this folder.
7. Run:
       pip install -r requirements.txt
8. Test the old command-line pipeline:
       python 4_main.py
9. Start the website API:
       uvicorn api:app --reload
10. Your Lovable website will later call:
       POST http://127.0.0.1:8000/ask

Request body:
       {"question":"Who was in the Oakridge photograph?"}

Response:
       {
         "answer": "...",
         "conflicts": [...],
         "records_found": 3
       }

IMPORTANT:
- Do not upload .env to GitHub.
- Do not put OPENAI_API_KEY in the Lovable/React frontend.
- schema.sql is only run in Supabase SQL Editor.
