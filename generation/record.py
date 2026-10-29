"""Cost estimate and the JSON record saved next to every generation (also failed ones)."""

import json
from datetime import datetime
from pathlib import Path

import settings
from pricing import Estimate, estimate_cost
from utils import (COMMON_ASPECT_RATIOS, closest_aspect_ratio, describe_size, file_size_mb,
                   video_duration, video_size)

NOT_CHARGED = Estimate(0.0, "not charged: failed, cancelled and NSFW requests are free")


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def video_info(path: Path) -> dict:
    return {
        "file": path.as_posix(),
        "seconds": round(video_duration(path), 2),
        "size_mb": round(file_size_mb(path), 2),
        "resolution": describe_size(video_size(path)),
    }


def cost_aspect_ratio(model_settings: dict, video: Path) -> str:
    """The output aspect ratio; for "adaptive" the ratio of the reference video."""
    ratio = model_settings.get("aspect_ratio", "adaptive")
    if ratio != "adaptive":
        return ratio
    size = video_size(video)
    return closest_aspect_ratio(size, COMMON_ASPECT_RATIOS) if size else "16:9"


def estimate(model_name, resolution, model_settings: dict, video: Path,
             output_s: float, input_s: float) -> Estimate:
    return estimate_cost(model_name, resolution, output_s, input_s,
                         cost_aspect_ratio(model_settings, video), settings.PRICE_MULTIPLIER)


def planned_estimate(model, resolution, model_settings: dict, video: Path) -> Estimate:
    """Before the run: input = uploaded seconds, output = duration (or same as input)."""
    input_s = min(video_duration(video), model.upload_seconds(settings.MAX_DURATION))
    output_s = model_settings.get("duration", input_s)
    return estimate(model.name, resolution, model_settings, video, output_s, input_s)


def cost_dict(cost: Estimate) -> dict:
    return {"usd": cost.usd, "detail": cost.detail, "approximate": True,
            "currency": "USD", "multiplier": settings.PRICE_MULTIPLIER}


def new_record(args, model, prompt_text: str, video: Path, images: list[Path],
               model_settings: dict, planned: Estimate) -> dict:
    return {
        "status": "started",
        "started_at": now(),
        "model": {"name": str(args.model), "endpoint": model.endpoint},
        "prompt": {"name": str(args.prompt), "text": prompt_text},
        "input": {
            "video": video_info(video),
            "images": [f.as_posix() for f in images],
            "muted": args.mute,
        },
        "parameters": model_settings,
        "estimated_cost_before": cost_dict(planned),
    }


def save_record(path: Path, record: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False, default=str),
                    encoding="utf-8")
    print(f"Record:     {path}")
    return path
