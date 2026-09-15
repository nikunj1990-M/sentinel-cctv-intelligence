"""Shared face-embedding helper (InsightFace buffalo_l, 512-dim ArcFace embeddings).
Runs on CPU (onnxruntime CPUExecutionProvider, no CUDA on this machine) - only invoked
per detected face on a throttled frame interval, not per frame, so CPU is fine."""
from insightface.app import FaceAnalysis

EMBED_DIM = 512

_app = None

def _load():
    global _app
    if _app is None:
        _app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
        _app.prepare(ctx_id=0, det_size=(640, 640))
    return _app

def get_faces(frame):
    """Return insightface Face objects (bbox, normed_embedding, det_score) found in a BGR frame."""
    return _load().get(frame)
