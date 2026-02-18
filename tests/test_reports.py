from pathlib import Path

from atlas.evaluate import evaluate_dataset, write_report_artifacts


def test_write_report_artifacts_creates_json_and_markdown(tmp_path: Path) -> None:
    report = evaluate_dataset(Path("data/gold/v0_slice.jsonl"))
    artifacts = write_report_artifacts(
        report=report,
        output_dir=tmp_path,
        label="noisy eval",
        timestamp="20260218T120000Z",
    )

    json_path = Path(artifacts["json"])
    md_path = Path(artifacts["markdown"])

    assert json_path.exists()
    assert md_path.exists()
    assert json_path.name == "20260218T120000Z_noisy-eval.json"
    assert md_path.name == "20260218T120000Z_noisy-eval.md"

    content = md_path.read_text(encoding="utf-8")
    assert "ATLAS Evaluation Report" in content
    assert "Core Metrics" in content
