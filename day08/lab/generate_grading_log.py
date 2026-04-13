import json
import os
from datetime import datetime
from rag_answer import rag_answer

print("Generating grading run log...")

# Read questions from both files
questions = []

with open("data/test_questions.json", "r", encoding="utf-8") as f:
    questions.extend(json.load(f))

with open("data/test_questions2.json", "r", encoding="utf-8") as f:
    questions.extend(json.load(f))

log = []
for q in questions:
    print(f"Processing question {q['id']}...")
    result = rag_answer(q["question"], retrieval_mode="hybrid", use_rerank=True, top_k_search=10, top_k_select=3, verbose=False)
    log.append({
        "id": q["id"],
        "question": q["question"],
        "answer": result["answer"],
        "sources": result["sources"],
        "chunks_retrieved": len(result["chunks_used"]),
        "retrieval_mode": result["config"]["retrieval_mode"],
        "timestamp": datetime.now().isoformat()
    })

os.makedirs("logs", exist_ok=True)
with open("logs/grading_run.json", "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=2)

print("Done generating logs/grading_run.json")
