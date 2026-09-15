"""Create/reset the Qdrant collection used for the mock eGujCop wanted-persons gallery."""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from face_embed import EMBED_DIM

COLLECTION = "wanted_faces"

client = QdrantClient(host="localhost", port=6333)
if client.collection_exists(COLLECTION):
    client.delete_collection(COLLECTION)
client.create_collection(
    collection_name=COLLECTION,
    vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
)
print(f"Qdrant collection '{COLLECTION}' ready (dim={EMBED_DIM}, cosine).")
