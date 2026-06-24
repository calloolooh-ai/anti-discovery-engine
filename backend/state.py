"""
Shared in-memory job state. Import from here to avoid circular imports.
"""

# job_id -> dict with stage, progress, eta_seconds, error, graph, gaps, export, ...
jobs: dict[str, dict] = {}
