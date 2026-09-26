"""ROCm-friendly OCR engine."""
from __future__ import annotations
import os
import re
from dataclasses import dataclass
from typing import Any
from PIL import Image
from preprocess import segment_text_lines

@dataclass
class OCRLine:
    text: str
    confidence: float
    box: tuple[int, int, int, int]

def clean_text(value: str) -> str:
    value = value.replace("<s>", " ").replace("</s>", " ")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()

class StubEngine:
    name = "stub"
    device = "cpu"
    def read(self, image: Image.Image):
        line = OCRLine("INFRALENS TEST", 1.0, (0, 0, image.width, image.height))
        return line.text, line.confidence, [line]

class TrOCREngine:
    name = "trocr"

    def __init__(self) -> None:
        import torch
        from transformers import AutoImageProcessor, RobertaTokenizer, VisionEncoderDecoderModel
        self.torch = torch
        self.model_id = os.environ.get("OCR_MODEL_ID", "microsoft/trocr-base-printed")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        cache = os.environ.get("HF_HOME", "/models")
        offline = os.environ.get("HF_HUB_OFFLINE", "0") in {"1", "true", "TRUE"}
        self.image_processor = AutoImageProcessor.from_pretrained(
            self.model_id, cache_dir=cache, local_files_only=offline
        )
        self.tokenizer = RobertaTokenizer.from_pretrained(
            self.model_id, cache_dir=cache, use_fast=False, local_files_only=offline
        )
        dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.model = VisionEncoderDecoderModel.from_pretrained(
            self.model_id, cache_dir=cache, torch_dtype=dtype, local_files_only=offline
        )
        self.model.to(self.device).eval()

    def _read_region(self, image: Image.Image) -> tuple[str, float]:
        torch = self.torch
        pixels = self.image_processor(image, return_tensors="pt").pixel_values.to(self.device)
        if self.device == "cuda":
            pixels = pixels.to(dtype=torch.float16)
        with torch.inference_mode():
            result = self.model.generate(
                pixels, max_new_tokens=48, num_beams=3, early_stopping=True,
                return_dict_in_generate=True, output_scores=True,
            )
        text = clean_text(self.tokenizer.batch_decode(result.sequences, skip_special_tokens=True)[0])
        confidence = 0.80 if text else 0.0
        try:
            transition = self.model.compute_transition_scores(
                result.sequences, result.scores, result.beam_indices, normalize_logits=True
            )
            probs = transition.exp()
            valid = probs[torch.isfinite(probs)]
            if valid.numel():
                confidence = float(valid.mean().item())
        except Exception:
            pass
        return text, max(0.0, min(1.0, confidence))

    def read(self, image: Image.Image):
        lines: list[OCRLine] = []
        for region in segment_text_lines(image):
            text, conf = self._read_region(region.image)
            if text:
                lines.append(OCRLine(text, conf, region.box))
        if not lines:
            return "", 0.0, []
        lines.sort(key=lambda x: (x.box[1], x.box[0]))
        text = "\n".join(line.text for line in lines)
        weights = [max(1, len(re.sub(r"\s+", "", line.text))) for line in lines]
        confidence = sum(l.confidence * w for l, w in zip(lines, weights)) / sum(weights)
        return clean_text(text), float(confidence), lines

_ENGINE: Any | None = None

def get_engine():
    global _ENGINE
    if _ENGINE is None:
        kind = os.environ.get("OCR_BACKEND", "trocr").lower()
        if kind == "stub":
            _ENGINE = StubEngine()
        elif kind == "trocr":
            _ENGINE = TrOCREngine()
        else:
            raise ValueError(f"Unsupported OCR_BACKEND={kind!r}")
    return _ENGINE

def runtime_metadata(engine: Any) -> dict[str, Any]:
    data: dict[str, Any] = {"engine": engine.name, "device": getattr(engine, "device", "unknown")}
    try:
        import torch
        data.update({
            "torch": torch.__version__,
            "hip": getattr(torch.version, "hip", None),
            "gpu_available": bool(torch.cuda.is_available()),
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        })
    except Exception:
        pass
    return data
