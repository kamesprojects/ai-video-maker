"""Approximate generation cost from pricing.json (list prices, before discounts)."""

import json
import math
from pathlib import Path
from typing import NamedTuple

PRICING_FILE = Path(__file__).parent / "pricing.json"


class Estimate(NamedTuple):
    usd: float | None   # None = no public price
    detail: str         # how it was calculated

    def __str__(self) -> str:
        return f"~${self.usd:.2f} ({self.detail})" if self.usd is not None else self.detail


def load_pricing(path: Path = PRICING_FILE) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))["models"]


def output_size(resolution: str, aspect_ratio: str) -> tuple[int, int]:
    """Approximate output width x height: "720p" + "9:16" -> (720, 1280)."""
    short = int(resolution.rstrip("p"))
    w, h = (int(n) for n in aspect_ratio.split(":"))
    long = round(short * max(w, h) / min(w, h))
    return (long, short) if w >= h else (short, long)


def estimate_cost(model: str, resolution: str, output_s: float, input_s: float,
                  aspect_ratio: str = "16:9", multiplier: float = 1.0,
                  pricing: dict | None = None) -> Estimate:
    """Approximate USD cost of one generation; multiplier = your discount, e.g. 0.8."""
    price = (pricing or load_pricing()).get(str(model), {})
    billing = price.get("billing")
    if billing == "per_second":
        estimate = per_second(price, resolution, output_s, input_s)
    elif billing == "video_tokens":
        estimate = video_tokens(price, resolution, output_s, input_s, aspect_ratio)
    else:
        return Estimate(None, f"unknown ({price.get('rule', 'no price in pricing.json')})")
    return Estimate(round(estimate.usd * multiplier, 4), estimate.detail)


def per_second(price: dict, resolution: str, output_s: float, input_s: float) -> Estimate:
    output_s = math.ceil(output_s) if price.get("round_output_up") else output_s
    input_s = input_s if price.get("bills_input_video") else 0
    rate = price["usd_per_second"][resolution]
    seconds = output_s + input_s
    return Estimate(seconds * rate, f"{output_s:.1f} s output + {input_s:.1f} s input x ${rate}/s")


def video_tokens(price: dict, resolution: str, output_s: float, input_s: float,
                 aspect_ratio: str) -> Estimate:
    w, h = output_size(resolution, aspect_ratio)
    seconds = output_s + (input_s if price.get("bills_input_video") else 0)
    tokens = math.ceil(w * h * seconds * price["tokens_per_pixel_second"])
    rate = price["usd_per_1000_tokens_with_video_input"][resolution]
    return Estimate(tokens / 1000 * rate,
                    f"{tokens:,} tokens ({w}x{h}, {seconds:.1f} s) x ${rate}/1000")
