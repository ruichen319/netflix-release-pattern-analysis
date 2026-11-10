"""Shared observation and candidate-window definitions used by every analysis."""

OBSERVATION_WEEKS = tuple(range(-12, 12))
CANDIDATE_WINDOWS = {"all_at_once": (-1, 5), "split_batches": (-1, 10)}
FORMAT_LABELS = {"all_at_once": "All-at-once", "split_batches": "Split release"}
