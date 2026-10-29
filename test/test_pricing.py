"""Cost estimates (pricing.py + pricing.json) and the JSON record (main.run)."""

import json
from pathlib import Path

import pytest

import generation.record as record_module
import main
import pricing
from choices import ModelName

PRICES = pricing.load_pricing()


# --- pricing.json ------------------------------------------------------------

def test_pricing_has_every_model():
    assert set(PRICES) == {str(m) for m in ModelName}


def test_pricing_endpoints_match_the_models():
    for name, model in main.MODELS.items():
        assert PRICES[str(name)]["endpoint"] == model.endpoint


# --- estimate_cost -----------------------------------------------------------

def test_wan_bills_output_plus_input_seconds():
    cost = pricing.estimate_cost("wan", "720p", output_s=10, input_s=10, pricing=PRICES)

    assert cost.usd == pytest.approx(2.00)   # 20 s x $0.10


def test_genjutsu_rounds_output_up():
    cost = pricing.estimate_cost("genjutsu-light", "480p", output_s=10.2, input_s=10,
                                 pricing=PRICES)

    assert cost.usd == pytest.approx(1.05)   # (11 + 10) s x $0.05


def test_seedance_uses_video_tokens():
    # ceil(720 x 1280 x 10 s x 24 / 1024) = 216,000 tokens x $0.01284 / 1000
    cost = pricing.estimate_cost("seedance", "720p", output_s=5, input_s=5,
                                 aspect_ratio="9:16", pricing=PRICES)

    assert cost.usd == pytest.approx(216_000 / 1000 * 0.01284, abs=0.001)
    assert "216,000 tokens (720x1280" in cost.detail


def test_kling_has_no_public_price():
    cost = pricing.estimate_cost("kling", "720p", 10, 10, pricing=PRICES)

    assert cost.usd is None
    assert "not available" in str(cost)


def test_multiplier_applies_a_discount():
    cost = pricing.estimate_cost("wan", "480p", 10, 10, multiplier=0.8, pricing=PRICES)

    assert cost.usd == pytest.approx(0.80)   # $1.00 x 0.8


@pytest.mark.parametrize("resolution, ratio, expected", [
    ("720p", "9:16", (720, 1280)),
    ("480p", "16:9", (853, 480)),
    ("1080p", "1:1", (1080, 1080)),
])
def test_output_size(resolution, ratio, expected):
    assert pricing.output_size(resolution, ratio) == expected


# --- JSON record from main.run() ----------------------------------------------

@pytest.fixture
def fake_run(tmp_path, monkeypatch):
    """main.run() with fake prepare/generate and video info. Returns a runner."""
    def fake_info(path):
        return {"file": Path(path).name, "seconds": 10.0, "size_mb": 1.0, "resolution": "720x1280"}

    monkeypatch.setattr(main, "OUT", tmp_path / "out")
    monkeypatch.setattr(main, "prepare_video", lambda video, *a, **k: video)
    monkeypatch.setattr(main, "video_info", fake_info)
    monkeypatch.setattr(record_module, "video_info", fake_info)
    monkeypatch.setattr(record_module, "video_size", lambda _: None)

    def _run(generate):
        monkeypatch.setattr(main, "generate", generate)
        args = main.Args(ModelName.WAN, "720p", "one-person", False, False)
        model = main.MODELS[ModelName.WAN]
        planned = pricing.Estimate(2.0, "planned")
        try:
            main.run(args, model, "text", Path("ref.mp4"), [Path("a.png")], {"duration": 10}, planned)
        finally:
            [record] = (tmp_path / "out").glob("*.json")
        return json.loads(record.read_text(encoding="utf-8")), record

    return _run


def test_completed_run_writes_json_with_video_and_cost(fake_run):
    def generate(model, prompt, video, images, settings, output, record):
        record.update(request_id="r1", status="completed")
        return output

    data, path = fake_run(generate)

    assert data["status"] == "completed"
    assert data["request_id"] == "r1"
    assert data["output"]["seconds"] == 10.0
    assert data["cost"]["usd"] == pytest.approx(2.00)   # wan 720p: (10 + 10) s x $0.10
    assert data["prompt"] == {"name": "one-person", "text": "text"}
    assert path.name.startswith("wan_720p_one-person_")


def test_failed_run_still_writes_json_with_zero_cost(fake_run):
    def generate(model, prompt, video, images, settings, output, record):
        record.update(request_id="r2", status="failed")
        raise SystemExit("Generation failed.")

    with pytest.raises(SystemExit):
        fake_run(generate)


def test_failed_run_json_content(fake_run, tmp_path):
    def generate(model, prompt, video, images, settings, output, record):
        record["status"] = "nsfw"
        raise SystemExit("Rejected by moderation (NSFW).")

    with pytest.raises(SystemExit):
        fake_run(generate)

    [path] = (tmp_path / "out").glob("*.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["status"] == "nsfw"
    assert data["cost"]["usd"] == 0.0
    assert "moderation" in data["error"]
    assert "output" not in data


def test_upload_error_is_recorded_as_error(fake_run, tmp_path):
    def generate(*a):
        raise ConnectionError("upload timed out")

    with pytest.raises(ConnectionError):
        fake_run(generate)

    [path] = (tmp_path / "out").glob("*.json")
    assert json.loads(path.read_text(encoding="utf-8"))["status"] == "error"
