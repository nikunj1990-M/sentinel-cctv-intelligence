"""Shared CLIP embedding helper (openai/clip-vit-base-patch32, 512-dim) used by the
video indexer and the /search API. Runs on CPU via torch - only invoked per detected
crop / per search query, not per frame, so no OpenVINO acceleration is needed here."""
import torch
from transformers import CLIPModel, CLIPProcessor

MODEL_NAME = "openai/clip-vit-base-patch32"
EMBED_DIM = 512

_model = None
_processor = None

def _load():
    global _model, _processor
    if _model is None:
        _processor = CLIPProcessor.from_pretrained(MODEL_NAME)
        _model = CLIPModel.from_pretrained(MODEL_NAME)
        _model.eval()
    return _model, _processor

def embed_image(pil_image):
    model, processor = _load()
    inputs = processor(images=pil_image, return_tensors="pt")
    with torch.no_grad():
        feats = model.get_image_features(**inputs).pooler_output
    feats = feats / feats.norm(p=2, dim=-1, keepdim=True)
    return feats[0].tolist()

def embed_text(text):
    model, processor = _load()
    inputs = processor(text=[text], return_tensors="pt", padding=True)
    with torch.no_grad():
        feats = model.get_text_features(**inputs).pooler_output
    feats = feats / feats.norm(p=2, dim=-1, keepdim=True)
    return feats[0].tolist()
