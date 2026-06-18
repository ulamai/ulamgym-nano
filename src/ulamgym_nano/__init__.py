"""UlamGym Nano: public verifier-backed RLVR environment."""

from .schema import PromptRow, VerifierRow, SubmissionRow, ScoreResult, RewardVector
from .rlvr import RLVRScorer
from .env import NanoEnv

__all__ = [
    "PromptRow",
    "VerifierRow",
    "SubmissionRow",
    "ScoreResult",
    "RewardVector",
    "RLVRScorer",
    "NanoEnv",
]

__version__ = "0.2.0"
