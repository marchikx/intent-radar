from pathlib import Path

from intent_radar.ats_ashby import load_fixture, parse_ashby_job
from intent_radar.gates import evaluate_gates
from intent_radar.normalize import normalize_job
from intent_radar.passport import build_passport
from intent_radar.score import compute_score

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "sample_ashby_job.json"


def test_passport_contains_source_quotes():
    board = load_fixture(FIXTURE)
    job = parse_ashby_job(board)
    lead = normalize_job(job, company_name="Acme Cloud Tools", headcount=42)
    gates = evaluate_gates(lead)
    score = compute_score(lead, gates)
    passport = build_passport(lead, gates, score)

    assert passport["quotes_from_source_only"]["title"] == job["title"]
    assert "n8n" in (passport["quotes_from_source_only"]["description_excerpt"] or "").lower()
    assert passport["score"]["value"] == score["score"]
    assert passport["gates"]["tool_keywords"]["result"] == "PASS"
