import logging
import os
import pickle
import time
from typing import List, Dict, Any, Optional

from src.core.models import ApiCard

logger = logging.getLogger(__name__)

class TextMatcher:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model_name = model_name
        self.model = None
        self.index: Dict[int, Any] = {} # card_id -> embedding
        self.index_path = os.path.join(os.getcwd(), "data", "db", "text_embeddings.pkl")
        self.card_names: Dict[int, str] = {} # card_id -> name (for quick lookup)

    def load_model(self):
        """Lazy loads the Sentence Transformer model."""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading Sentence Transformer model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
            except Exception as e:
                logger.error(f"Failed to load Sentence Transformer: {e}")
                self.model = None

    def _construct_text(self, card: ApiCard) -> str:
        """Constructs the text representation for embedding."""
        # id | name | set_code | desc | typeline | atk | def | Linkval

        parts = []
        parts.append(str(card.id))
        parts.append(card.name)

        # Set Codes
        if card.card_sets:
            codes = " ".join([s.set_code for s in card.card_sets])
            parts.append(f"Sets: {codes}")

        parts.append(card.desc)

        # Typeline / Type / Race
        if card.typeline:
            parts.append(" ".join(card.typeline))
        else:
            if card.type: parts.append(card.type)
            if card.race: parts.append(card.race)

        # ATK / DEF
        if card.atk is not None:
            parts.append(f"ATK/{card.atk}")
        if card.def_ is not None:
            parts.append(f"DEF/{card.def_}")

        # Linkval
        if card.linkval is not None:
            parts.append(f"Link-{card.linkval}")

        return " | ".join(parts)

    def build_index(self, cards: List[ApiCard], force_rebuild: bool = False):
        """Builds or loads the embedding index."""
        if not force_rebuild and os.path.exists(self.index_path):
            self.load_index()
            # If loaded successfully and has items, we might assume it's good.
            # But checking if we have enough items?
            # For now, simplistic check.
            if self.index:
                return

        self.load_model()
        if self.model is None:
            return

        logger.info(f"Building Text Embedding Index for {len(cards)} cards...")
        start_time = time.time()

        texts = []
        ids = []

        # Clear existing
        self.index = {}
        self.card_names = {}

        for card in cards:
            text = self._construct_text(card)
            texts.append(text)
            ids.append(card.id)
            self.card_names[card.id] = card.name

        if not texts:
            return

        # Batch Encode
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)

            self.index = {card_id: emb for card_id, emb in zip(ids, embeddings)}

            # Save
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            with open(self.index_path, "wb") as f:
                pickle.dump({"index": self.index, "names": self.card_names}, f)

            logger.info(f"Built index in {time.time() - start_time:.2f}s")

        except Exception as e:
            logger.error(f"Error building index: {e}")

    def load_index(self):
        """Loads the index from disk."""
        if not os.path.exists(self.index_path):
            return

        try:
            with open(self.index_path, "rb") as f:
                data = pickle.load(f)
                self.index = data.get("index", {})
                self.card_names = data.get("names", {})
            logger.info(f"Loaded Text Embedding Index: {len(self.index)} items")
        except Exception as e:
            logger.error(f"Failed to load index: {e}")

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Searches the index for the query text."""
        if not self.index:
            logger.warning("Index empty, cannot search.")
            return []

        self.load_model()
        if self.model is None:
            return []

        try:
            from sentence_transformers import util
            import torch
            import numpy as np

            # Encode Query
            query_emb = self.model.encode(query, convert_to_tensor=True)

            ids = list(self.index.keys())
            # Embeddings in index are numpy arrays
            # We need to make sure they are consistent.
            embeddings = np.array(list(self.index.values()))
            corpus_emb = torch.from_numpy(embeddings)

            # Move to same device as query_emb if needed (usually query_emb determines device)
            # sentence_transformers usually handles this.

            # Compute similarity
            scores = util.cos_sim(query_emb, corpus_emb)[0]

            # Get Top K
            k = min(top_k, len(scores))
            top_results = torch.topk(scores, k=k)

            results = []
            for score, idx in zip(top_results.values, top_results.indices):
                card_id = ids[idx.item()]
                name = self.card_names.get(card_id, "Unknown")

                results.append({
                    "card_id": card_id,
                    "name": name,
                    "score": float(score.item())
                })

            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
