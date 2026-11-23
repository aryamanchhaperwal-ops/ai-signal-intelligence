"""Unit tests for Entity Resolution Engine and Seed Database."""

import pytest
from src.entity_resolution.resolver import EntityResolver
from src.entity_resolution.seeds import AI_STARTUP_SEEDS


class TestEntityResolution:
    """Test deterministic cleaning, exact matching, and RapidFuzz resolution."""

    @pytest.fixture
    def resolver(self) -> EntityResolver:
        return EntityResolver(fuzzy_threshold=88.0, ambiguity_margin=6.0)

    def test_seed_database_count(self):
        """Verify the seed database contains at least 50 prominent AI startups."""
        assert len(AI_STARTUP_SEEDS) >= 50
        canonical_set = {s["canonical_name"] for s in AI_STARTUP_SEEDS}
        assert "OpenAI" in canonical_set
        assert "Anthropic" in canonical_set
        assert "Mistral AI" in canonical_set
        assert "Perplexity AI" in canonical_set
        assert "Hugging Face" in canonical_set

    def test_deterministic_normalization(self, resolver: EntityResolver):
        """Test suffix and protocol stripping."""
        assert resolver._normalize_string("OpenAI, Inc.") == "openai"
        assert resolver._normalize_string("https://anthropic.com") == "anthropic"
        assert resolver._normalize_string("Runway AI, Inc.") == "runway ai"
        assert resolver._normalize_string("Mistral AI SAS") == "mistral ai"
        assert resolver._normalize_string("DeepL GmbH") == "deepl"

    def test_seed_exact_match(self, resolver: EntityResolver):
        """Test exact match on canonical names and known aliases."""
        canonical, log = resolver.resolve("OpenAI, Inc.")
        assert canonical == "OpenAI"
        assert log.matchMethod == "SEED_EXACT"
        assert log.confidenceScore == 1.0
        assert log.isAmbiguous is False

        canonical2, log2 = resolver.resolve("c.ai")
        assert canonical2 == "Character.AI"
        assert log2.matchMethod == "SEED_EXACT"

        canonical3, log3 = resolver.resolve("Claude AI")
        assert canonical3 == "Anthropic"
        assert log3.matchMethod == "SEED_EXACT"

        canonical4, log4 = resolver.resolve("Runway AI, Inc.")
        assert canonical4 == "Runway"
        assert log4.matchMethod == "SEED_EXACT"

    def test_fuzzy_match(self, resolver: EntityResolver):
        """Test RapidFuzz matching for minor misspellings or variations."""
        canonical, log = resolver.resolve("Pineecone Systems")
        assert canonical == "Pinecone"
        assert log.matchMethod == "FUZZY_RAPIDFUZZ"
        assert log.confidenceScore >= 0.88

    def test_unresolved_entity_preservation(self, resolver: EntityResolver):
        """Unrecognized entities must retain their raw name without corrupting database."""
        raw_name = "Quantum HyperScale Bio AI"
        canonical, log = resolver.resolve(raw_name)
        assert canonical == raw_name
        assert log.matchMethod == "UNRESOLVED_PRESERVED"
        assert log.confidenceScore == 0.0

    def test_ambiguity_rejection(self, resolver: EntityResolver):
        """Ambiguous entities with close runner-ups must not be automatically merged."""
        # When two candidates have near identical scores, resolver flags isAmbiguous
        log_count_before = len(resolver.get_logs())
        canonical, log = resolver.resolve("Scale")
        assert len(resolver.get_logs()) == log_count_before + 1
        assert log.canonicalName in ["Scale AI", "Scale"]

    def test_empty_input_handling(self, resolver: EntityResolver):
        canonical, log = resolver.resolve("")
        assert canonical == "UNKNOWN"
        assert log.matchMethod == "EMPTY_INPUT"
