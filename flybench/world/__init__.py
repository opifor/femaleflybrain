"""Geometry-only world; neural controllers live in world.loop."""
from .arena import Arena, Body, Observation

__all__ = ["Arena", "Body", "Observation"]
