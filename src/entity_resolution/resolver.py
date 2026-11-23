"""Entity Resolution Engine.

Implements deterministic normalization, seed database exact matching, RapidFuzz
fuzzy matching, ambiguity detection, and audit log generation.
"""

import re
from typing import Dict, List, Optional, Tuple
from rapidfuzz import fuzz, process
from src.entity_resolution.seeds import AI_STARTUP_SEEDS, StartupSeed
from src.validation.schemas import EntityResolutionLog


class EntityResolver:
    """Production entity resolution engine for deduplication and canonical mapping."""

    def __init__(self, fuzzy_threshold: float = 88.0, ambiguity_margin: float = 6.0) -> None:
        """Initialize resolver with seed database and index.

        Args:
            fuzzy_threshold: Minimum RapidFuzz similarity score (0-100) to accept a fuzzy match.
            ambiguity_margin: Score delta below which close matches are flagged as ambiguous.
        """
        self.fuzzy_threshold = fuzzy_threshold
        self.ambiguity_margin = ambiguity_margin
        self.resolution_log: List[EntityResolutionLog] = []

        # Canonical lookup indices
        self.canonical_names: List[str] = []
        self._exact_map: Dict[str, str] = {}
        self._build_index()

    def _normalize_string(self, text: str) -> str:
        """Apply deterministic cleaning to standardize company/product names."""
        if not text:
            return ""
        norm = text.lower().strip()

        # Remove web protocols and standard domain extensions
        norm = re.sub(r"https?://(www\.)?", "", norm)
        norm = re.sub(r"\.(com|ai|io|co|tech|net|org|app|dev)/?$", "", norm)

        # Remove legal corporate suffixes
        legal_suffixes = [
            r"\binc\.?", r"\bllc\.?", r"\bltd\.?", r"\bcorp(\.|oration)?\b",
            r"\bpbc\b", r"\bgmbh\b", r"\bsas\b", r"\bse\b", r"\bco\.?", r"\bs\.a\b"
        ]
        for pattern in legal_suffixes:
            norm = re.sub(pattern, "", norm)

        # Remove punctuation, symbols, and excess spaces
        norm = re.sub(r"[^\w\s]", " ", norm)
        norm = re.sub(r"\s+", " ", norm).strip()
        return norm

    def _build_index(self) -> None:
        """Index all canonical startup seeds and their aliases."""
        for seed in AI_STARTUP_SEEDS:
            canonical = seed["canonical_name"]
            if canonical not in self.canonical_names:
                self.canonical_names.append(canonical)

            # Map normalized canonical name
            norm_canonical = self._normalize_string(canonical)
            self._exact_map[norm_canonical] = canonical

            # Map all normalized aliases
            for alias in seed["aliases"]:
                norm_alias = self._normalize_string(alias)
                self._exact_map[norm_alias] = canonical

    def resolve(self, raw_name: str) -> Tuple[str, EntityResolutionLog]:
        """Resolve a raw company or product name to its canonical counterpart.

        Args:
            raw_name: Input entity string as collected from source.

        Returns:
            Tuple of (assigned_canonical_name, resolution_log_entry).
        """
        if not raw_name or not raw_name.strip():
            log = EntityResolutionLog(
                rawName=raw_name or "UNKNOWN",
                canonicalName="UNKNOWN",
                matchMethod="EMPTY_INPUT",
                confidenceScore=0.0,
                isAmbiguous=False
            )
            self.resolution_log.append(log)
            return "UNKNOWN", log

        normalized = self._normalize_string(raw_name)

        # 1. Deterministic Exact Lookup (Fast Path)
        if normalized in self._exact_map:
            canonical = self._exact_map[normalized]
            log = EntityResolutionLog(
                rawName=raw_name,
                canonicalName=canonical,
                matchMethod="SEED_EXACT",
                confidenceScore=1.0,
                isAmbiguous=False
            )
            self.resolution_log.append(log)
            return canonical, log

        # 2. Fuzzy Matching against canonical database
        matches = process.extract(
            query=normalized,
            choices=list(self._exact_map.keys()),
            scorer=fuzz.token_sort_ratio,
            limit=2
        )

        if matches:
            best_match, best_score, _ = matches[0]

            # Check if match meets confidence threshold
            if best_score >= self.fuzzy_threshold:
                # Check for ambiguity with the second match
                is_ambiguous = False
                if len(matches) > 1:
                    second_match, second_score, _ = matches[1]
                    if (best_score - second_score) <= self.ambiguity_margin and best_score < 96.0:
                        is_ambiguous = True

                if is_ambiguous:
                    # Do not automatically merge ambiguous entities
                    log = EntityResolutionLog(
                        rawName=raw_name,
                        canonicalName=raw_name.strip(),
                        matchMethod="AMBIGUOUS_REJECTED",
                        confidenceScore=best_score / 100.0,
                        isAmbiguous=True
                    )
                    self.resolution_log.append(log)
                    return raw_name.strip(), log

                canonical = self._exact_map[best_match]
                log = EntityResolutionLog(
                    rawName=raw_name,
                    canonicalName=canonical,
                    matchMethod="FUZZY_RAPIDFUZZ",
                    confidenceScore=best_score / 100.0,
                    isAmbiguous=False
                )
                self.resolution_log.append(log)
                return canonical, log

        # 3. Unresolved Entity (Preserve raw title-cased name)
        fallback_canonical = raw_name.strip()
        log = EntityResolutionLog(
            rawName=raw_name,
            canonicalName=fallback_canonical,
            matchMethod="UNRESOLVED_PRESERVED",
            confidenceScore=0.0,
            isAmbiguous=False
        )
        self.resolution_log.append(log)
        return fallback_canonical, log

    def get_logs(self) -> List[EntityResolutionLog]:
        """Retrieve full audit log history for export."""
        return self.resolution_log
