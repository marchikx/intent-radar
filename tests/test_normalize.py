from pathlib import Path

from intent_radar.ats_ashby import load_fixture, parse_ashby_job
from intent_radar.normalize import normalize_job

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "sample_ashby_job.json"


def test_normalize_job_from_fixture():
    board = load_fixture(FIXTURE)
    job = parse_ashby_job(board)
    lead = normalize_job(job, company_name="Acme Cloud Tools", headcount=42)

    assert lead["company"]["name"] == "Acme Cloud Tools"
    assert lead["company"]["headcount"] == 42
    assert "Workflow Automation" in lead["role"]["title"]
    assert lead["location"].startswith("Remote")
    assert lead["compensation"]["pay_signal_present"] is True
    assert lead["compensation"]["amount"] == 100000.0
    assert "n8n" in lead["evidence"]["description_quote"].lower()
