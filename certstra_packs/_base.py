#!/usr/bin/env python3
"""Shared helpers for certification packs. A pack exposes MANIFEST + stage functions + SAMPLES.

Stage → function it must provide:
  certify -> checks(packet, P) -> list[CheckResult]   (kernel certify() merges by severity)
  stage   -> schedule(release, P) -> list[stage_step] (kernel plan_stages() plans rollout)
"""

from certstra_core.verdict import certifiable, needs_review, blocked

__all__ = ["certifiable", "needs_review", "blocked"]
