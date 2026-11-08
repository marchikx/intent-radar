from pathlib import Path

from intent_radar.ats_ashby import load_fixture, parse_ashby_job
from intent_radar.gates import evaluate_gates
from intent_radar.normalize import normalize_job
from intent_radar.score import compute_score

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "sample_ashby_job.json"


def test_score_high_when_gates_pass():
    board = load_fixture(FIXTURE)
    job = parse_ashby_job(board)
    lead = normalize_job(job, company_name="Acme Cloud Tools", headcount=42)
    gates = evaluate_gates(lead)
    result = compute_score(lead, gates)

    assert result["score"] >= 90
    assert result["all_gates_pass"] is True
    assert any(b["gate"] == "pay_signal" and b["earned"] == 35 for b in result["breakdown"])
