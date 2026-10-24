"""Research module for VideoAutomater."""

from videoautomater.research.agent import ContentResearchAgent
from videoautomater.research.registry import TopicRegistry
from videoautomater.research.verifier import EvidenceVerifier

__all__ = ["ContentResearchAgent", "EvidenceVerifier", "TopicRegistry"]
