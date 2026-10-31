from pathlib import Path

from src.parsers import parse_bola, parse_semgrep, parse_zap

FIXTURES = Path(__file__).parent / "fixtures"


def test_semgrep_parser_normalizes_result():
    finding = parse_semgrep(FIXTURES / "semgrep.json", "S0")[0]
    assert finding["condition"] == "S0"
    assert finding["severity"] == "medium"
    assert finding["classification"] == "unverified"


def test_zap_parser_normalizes_nested_report():
    finding = parse_zap(FIXTURES / "zap.json")[0]
    assert finding["condition"] == "D0"
    assert finding["rule_id"] == "10021"
    assert finding["severity"] == "low"


def test_bola_parser_uses_oracle():
    finding = parse_bola(FIXTURES / "bola.json")[0]
    assert finding["condition"] == "D1"
    assert finding["classification"] == "true_positive"
    assert finding["scenario_ids"] == ["CRAPI-BOLA-VEHICLE-LOCATION"]

