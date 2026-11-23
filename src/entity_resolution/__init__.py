"""Entity resolution package exports."""

from src.entity_resolution.resolver import EntityResolver
from src.entity_resolution.seeds import AI_STARTUP_SEEDS, StartupSeed

__all__ = ["EntityResolver", "AI_STARTUP_SEEDS", "StartupSeed"]
