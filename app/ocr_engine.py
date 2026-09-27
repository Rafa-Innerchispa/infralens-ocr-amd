"""Qwen2.5-VL OCR engine with bounded test-time augmentation."""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps, ImageStat

from challenge_rules import SYSTEM_PROMPT, USER_PROMPT, clean_text, vote_key

DEFAULT_MODEL_ID = "Qwen/Qwen2.5-VL-3B-Instruct"

@dataclass
class Candidate:
    text: str
    probability: float
    variant: str
    complete: bool

class StubEngine:
    name = "stub"
    device = "cpu"

    def warmup(self) -> None:
        return

    def read(self, _image: Image.Image) -> tuple[str, float, dict[str, Any]]:
        return "INFRALENS TEST", 1.0, {
            "passes": 1,
            "agreement": 1.0,
            "candidates": ["INFRALENS TEST"],
            "variants": ["stub"],
        }

def prepare_image(image: Image.Image, max_side: int = 1280, min_side: int = 640) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGB")
    w, h = image.size
    longest = max(w, h)
    scale = 1.0
    if longest > max_side:
        scale = max_side / longest
    elif longest < min_side:
        scale = min_side / max(longest, 1)
    if scale != 1.0:
        image = image.resize(
            (max(1, round(w * scale)), max(1, round(h * scale))),
            Image.Resampling.LANCZOS,
        )
    return image

def _brightness(image: Image.Image) -> float:
    return float(ImageStat.Stat(image.convert("L")).mean[0])

def _noise_score(image: Image.Image) -> float:
    gray = image.convert("L")
    median = gray.filter(ImageFilter.MedianFilter(3))
    diff = ImageChops.difference(gray, median)
    return float(ImageStat.Stat(diff).mean[0])

def image_variants(image: Image.Image, count: int) -> list[tuple[str, Image.Image]]:
    image = prepare_image(image)
    out = [("original", image)]
    if count <= 1:
        return out

    base = image
    if _noise_score(image) > 8.5:
        base = image.filter(ImageFilter.MedianFilter(3))
    if _brightness(base) < 85:
        base = ImageEnhance.Brightness(base).enhance(1.55)

    contrast = ImageOps.autocontrast(base, cutoff=1)
    out.append(("contrast", contrast))
    if count >= 3:
        out.append(("sharp", ImageEnhance.Sharpness(contrast).enhance(2.0)))
    return out[:count]

def generation_complete(
    token_ids: list[int],
    eos_token_id: int | list[int] | tuple[int, ...] | set[int] | None,
    max_new_tokens: int,
) -> bool:
    """Fail closed only when generation exhausts its token budget without EOS."""
    if not token_ids:
        return True
    if eos_token_id is None:
        eos_ids: set[int] = set()
    elif isinstance(eos_token_id, (list, tuple, set)):
        eos_ids = {int(value) for value in eos_token_id}
    else:
        eos_ids = {int(eos_token_id)}
    if eos_ids and int(token_ids[-1]) in eos_ids:
        return True
    return len(token_ids) < max_new_tokens

class QwenOCREngine:
    name = "qwen2.5-vl-3b"

    def __init__(self) -> None:
        import torch
        from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

        self.torch = torch
        self.model_id = os.environ.get("MODEL_ID", DEFAULT_MODEL_ID)
        default_dir = f"/models/{self.model_id.split('/')[-1]}"
        self.model_dir = os.environ.get("MODEL_DIR", default_dir)
        source = self.model_dir if Path(self.model_dir).is_dir() else self.model_id
        local = Path(source).is_dir()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        requested = os.environ.get(
            "OCR_DTYPE", "bf16" if self.device == "cuda" else "fp32"
        ).lower()
        dtype = {
            "bf16": torch.bfloat16,
            "fp16": torch.float16,
            "fp32": torch.float32,
        }.get(requested, torch.bfloat16)

        min_pixels = int(os.environ.get("OCR_MIN_PIXELS", str(256 * 28 * 28)))
        max_pixels = int(os.environ.get("OCR_MAX_PIXELS", str(1280 * 28 * 28)))

        self.processor = AutoProcessor.from_pretrained(
            source,
            min_pixels=min_pixels,
            max_pixels=max_pixels,
            local_files_only=local,
        )
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            source,
            torch_dtype=dtype,
            local_files_only=local,
            attn_implementation="sdpa",
        )
        self.model.to(self.device).eval()

        self.tta_passes = max(
            1, min(3, int(os.environ.get("OCR_TTA_PASSES", "3")))
        )
        self.time_budget_s = float(os.environ.get("OCR_TIME_BUDGET_S", "20"))
        self.max_new_tokens = max(
            64, min(512, int(os.environ.get("OCR_MAX_NEW_TOKENS", "256")))
        )

    def warmup(self) -> None:
        from PIL import ImageDraw

        image = Image.new("RGB", (640, 320), "white")
        ImageDraw.Draw(image).text((180, 140), "STOP", fill="black")
        self._generate(image)

    def _generate(self, image: Image.Image) -> tuple[str, float, bool]:
        import torch
        from qwen_vl_utils import process_vision_info

        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": SYSTEM_PROMPT}],
            },
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": USER_PROMPT},
                ],
            },
        ]
        prompt = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = self.processor(
            text=[prompt],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        ).to(self.device)

        with torch.inference_mode():
            output = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                num_beams=1,
                return_dict_in_generate=True,
                output_scores=True,
            )

        prompt_len = inputs["input_ids"].shape[1]
        generated = output.sequences[0, prompt_len:]
        token_ids = [int(value) for value in generated.tolist()]
        eos_token_id = getattr(self.model.generation_config, "eos_token_id", None)
        if eos_token_id is None and hasattr(self.processor, "tokenizer"):
            eos_token_id = getattr(self.processor.tokenizer, "eos_token_id", None)
        complete = generation_complete(
            token_ids,
            eos_token_id,
            self.max_new_tokens,
        )
        raw = self.processor.batch_decode(
            [generated],
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )[0]

        probabilities: list[float] = []
        try:
            for logits, token_id in zip(output.scores, generated.tolist()):
                probabilities.append(
                    float(torch.softmax(logits[0].float(), dim=-1)[token_id].item())
                )
        except Exception:
            probabilities = []
        confidence = (
            sum(probabilities) / len(probabilities) if probabilities else 0.5
        )
        return raw, float(max(0.0, min(1.0, confidence))), complete

    def read(self, image: Image.Image) -> tuple[str, float, dict[str, Any]]:
        started = time.monotonic()
        candidates: list[Candidate] = []

        for index, (name, variant) in enumerate(
            image_variants(image, self.tta_passes)
        ):
            elapsed = time.monotonic() - started
            if index > 0:
                average = elapsed / index
                if elapsed + average >= self.time_budget_s:
                    break

            raw, probability, complete = self._generate(variant)
            candidates.append(
                Candidate(
                    text=clean_text(raw),
                    probability=probability,
                    variant=name,
                    complete=complete,
                )
            )

        if not candidates:
            return "", 0.0, {
                "passes": 0,
                "agreement": 0.0,
                "candidates": [],
                "variants": [],
            }

        complete_candidates = [candidate for candidate in candidates if candidate.complete]
        if not complete_candidates:
            return "", 0.0, {
                "passes": len(candidates),
                "eligible_passes": 0,
                "agreement": 0.0,
                "generation_complete": False,
                "truncated_passes": len(candidates),
                "candidates": [c.text for c in candidates],
                "variants": [c.variant for c in candidates],
            }

        groups: dict[str, list[Candidate]] = {}
        for candidate in complete_candidates:
            groups.setdefault(vote_key(candidate.text), []).append(candidate)

        def rank(group: list[Candidate]) -> tuple[int, float, int]:
            mean_probability = (
                sum(c.probability for c in group) / len(group)
            )
            return (
                len(group),
                mean_probability,
                1 if vote_key(group[0].text) else 0,
            )

        best_group = max(groups.values(), key=rank)
        best = max(best_group, key=lambda c: c.probability)
        agreement = len(best_group) / len(complete_candidates)
        mean_probability = (
            sum(c.probability for c in best_group) / len(best_group)
        )
        confidence = max(
            0.0,
            min(1.0, mean_probability * (0.65 + 0.35 * agreement)),
        )

        return best.text, round(confidence, 4), {
            "passes": len(candidates),
            "eligible_passes": len(complete_candidates),
            "agreement": round(agreement, 3),
            "elapsed_s": round(time.monotonic() - started, 3),
            "generation_complete": True,
            "truncated_passes": len(candidates) - len(complete_candidates),
            "candidates": [c.text for c in candidates],
            "variants": [c.variant for c in candidates],
        }

_ENGINE: Any | None = None

def get_engine():
    global _ENGINE
    if _ENGINE is None:
        backend = os.environ.get("OCR_BACKEND", "qwen").lower()
        _ENGINE = StubEngine() if backend == "stub" else QwenOCREngine()
    return _ENGINE

def runtime_metadata(engine: Any) -> dict[str, Any]:
    data = {
        "engine": engine.name,
        "device": getattr(engine, "device", "unknown"),
        "model_id": getattr(engine, "model_id", None),
        "max_new_tokens": getattr(engine, "max_new_tokens", None),
        "tta_passes": getattr(engine, "tta_passes", None),
    }
    try:
        import torch
        data.update({
            "torch": torch.__version__,
            "hip": getattr(torch.version, "hip", None),
            "gpu_available": bool(torch.cuda.is_available()),
            "gpu_name": (
                torch.cuda.get_device_name(0)
                if torch.cuda.is_available()
                else None
            ),
        })
    except Exception:
        pass
    return data
