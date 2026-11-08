"""Intent radar — offline ATS job parsing, gates, scoring, and evidence passports."""

from intent_radar.ats_ashby import load_fixture, parse_ashby_job
from intent_radar.gates import GateResult, evaluate_gates
from intent_radar.normalize import normalize_job
from intent_radar.passport import build_passport
from intent_radar.score import compute_score

__all__ = [
    "load_fixture",
    "parse_ashby_job",
    "normalize_job",
    "evaluate_gates",
    "GateResult",
    "build_passport",
    "compute_score",
]

__version__ = "0.1.0"
