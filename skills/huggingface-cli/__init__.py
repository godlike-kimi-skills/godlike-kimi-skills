# -*- coding: utf-8 -*-
"""
HuggingFace CLI Skill
=====================

A command-line tool for managing HuggingFace models and datasets.

Example:
    >>> from main import HuggingFaceCLI
    >>> cli = HuggingFaceCLI()
    >>> cli.search_models("bert-base-chinese", limit=5)

Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Kimi Code CLI"
__license__ = "MIT"

from main import HuggingFaceCLI

__all__ = ["HuggingFaceCLI"]
