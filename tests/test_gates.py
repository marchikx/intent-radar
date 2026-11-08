from pathlib import Path

from intent_radar.ats_ashby import load_fixture, parse_ashby_job
from intent_radar.gates import FAIL, PASS, all_pass, evaluate_gates
from intent_radar.normalize import normalize_job

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "sample_ashby_job.json"


def _sample_lead():
    board = load_fixture(FIXTURE)
    job = parse_ashby_job(board)
    return normalize_job(job, company_name="Acme Cloud Tools", headcount=42)


def test_gates_pass_on_fixture_lead():
    lead = _sample_lead()
    results = evaluate_gates(lead)
    assert results["pay_signal"].result == PASS
    assert results["tool_keywords"].result == PASS
    assert results["headcount_band"].result == PASS
    assert all_pass(results)


def test_headcount_gate_fails_out_of_band():
    lead = _sample_lead()
    lead["company"]["headcount"] = 5
    results = evaluate_gates(lead)
    assert results["headcount_band"].result == FAIL
