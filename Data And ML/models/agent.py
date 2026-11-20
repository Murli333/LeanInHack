"""
Direct export for ScamInvestigatorAgent from models package.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from agent import ScamInvestigatorAgent, get_agent

__all__ = ["ScamInvestigatorAgent", "get_agent"]
