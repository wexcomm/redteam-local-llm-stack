#!/usr/bin/env python3
"""
Document Watchdog — Auto-ingest files into PrivateGPT RAG

Inspired by the Hermes Ollama Agent "Deal Monitor" pattern:
- Watches a directory for new/modified files
- Auto-ingests them via PrivateGPT API
- Scores documents by sensitivity keywords
- Logs all activity

Usage:
    python3 document-watchdog.py --watch ~/threat-intel --api http://localhost:8281

Requirements:
    pip install watchdog requests
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Set

import requests
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


# Sensitivity scoring — adjust to your needs
SENSITIVITY_KEYWORDS = {
    "critical": ["0day", "zero-day", "exploit", "shellcode", "payload", "backdoor", "rootkit"],
    "high": ["CVE-", "vulnerability", "APT", "malware", "ransomware", "breach", "leak"],
    "medium": ["pentest", "penetration", "red team", "offensive", "reverse engineering"],
}

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".docx", ".json", ".csv", ".log", ".xml", ".html"}


class DocumentScorer:
    """Score documents by sensitivity based on keywords."""

    def score(self, filepath: Path) -> dict:
        """Return sensitivity score and matched keywords."""
        score = {"level": "low", "score": 0.0, "matches": []}

        try:
            # Read first 50KB for keyword scanning
            content = filepath.read_text(errors="replace")[:50000]
            content_lower = content.lower()
        except Exception as e:
            return {**score, "error": str(e)}

        total_weight = 0
        for level, keywords in SENSITIVITY_KEYWORDS.items():
            weight = {"critical": 10, "high": 5, "medium": 2}.get(level, 1)
            for kw in keywords:
                if kw.lower() in content_lower:
                    total_weight += weight
                    score["matches"].append(f"{level}:{kw}")

        # Normalize to 0-10 scale
        normalized = min(total_weight, 10)
        score["score"] = normalized

        if normalized >= 7:
            score["level"] = "critical"
        elif normalized >= 4:
            score["level"] = "high"
        elif normalized >= 1:
            score["level"] = "medium"

        return score


class PrivateGPTIngestor:
    """Client for PrivateGPT ingestion API."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.ingest_url = f"{self.base_url}/v1/ingest"
        self.list_url = f"{self.base_url}/v1/ingest/list"

    def ingest(self, filepath: Path) -> dict:
        """Upload a file to PrivateGPT for ingestion."""
        try:
            with open(filepath, "rb") as f:
                files = {"file": (filepath.name, f, "application/octet-stream")}
                response = requests.post(
                    self.ingest_url,
                    files=files,
                    timeout=120,
                )
                response.raise_for_status()
                return {"success": True, "data": response.json()}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": f"Cannot connect to PrivateGPT at {self.base_url}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_ingested(self) -> List[str]:
        """List already-ingested documents."""
        try:
            response = requests.get(self.list_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            return [d.get("doc_id", "") for d in data.get("data", [])]
        except Exception:
            return []


class IngestEventHandler(FileSystemEventHandler):
    """Watchdog handler that ingests new files."""

    def __init__(
        self,
        ingestor: PrivateGPTIngestor,
        scorer: DocumentScorer,
        logger: logging.Logger,
        processed: Set[str],
        sensitivity_keywords: Optional[List[str]] = None,
    ):
        self.ingestor = ingestor
        self.scorer = scorer
        self.logger = logger
        self.processed = processed
        self.sensitivity_keywords = sensitivity_keywords or []

    def on_created(self, event):
        if event.is_directory:
            return
        self._handle_file(Path(event.src_path))

    def on_modified(self, event):
        if event.is_directory:
            return
        self._handle_file(Path(event.src_path))

    def _handle_file(self, filepath: Path):
        # Skip unsupported extensions
        if filepath.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return

        # Skip hidden/temp files
        if filepath.name.startswith(".") or filepath.name.startswith("~"):
            return

        # Skip already processed
        file_id = f"{filepath.stat().st_ino}:{filepath.stat().st_mtime}"
        if file_id in self.processed:
            return

        self.logger.info(f"Detected: {filepath}")

        # Score sensitivity
        sensitivity = self.scorer.score(filepath)
        self.logger.info(
            f"Sensitivity: {sensitivity['level'].upper()} ({sensitivity['score']}/10)"
        )
        if sensitivity["matches"]:
            self.logger.info(f"Keywords matched: {', '.join(sensitivity['matches'])}")

        # Ingest
        self.logger.info(f"Ingesting into PrivateGPT...")
        result = self.ingestor.ingest(filepath)

        if result["success"]:
            self.processed.add(file_id)
            self.logger.info(f"✅ Ingested: {filepath.name}")
        else:
            self.logger.error(f"❌ Failed: {result.get('error', 'Unknown error')}")


def setup_logging(log_file: Optional[str] = None):
    """Configure logging."""
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=handlers,
    )
    return logging.getLogger("watchdog")


def main():
    parser = argparse.ArgumentParser(description="Auto-ingest documents into PrivateGPT RAG")
    parser.add_argument("--watch", required=True, help="Directory to watch")
    parser.add_argument("--api", default="http://localhost:8281", help="PrivateGPT API base URL")
    parser.add_argument("--log", default="watchdog.log", help="Log file path")
    parser.add_argument(
        "--sensitivity-keywords",
        nargs="+",
        default=[],
        help="Additional keywords to flag as sensitive",
    )
    parser.add_argument(
        "--recursive", action="store_true", default=True, help="Watch subdirectories"
    )
    args = parser.parse_args()

    watch_dir = Path(args.watch).resolve()
    if not watch_dir.exists():
        print(f"Error: Directory does not exist: {watch_dir}")
        sys.exit(1)

    logger = setup_logging(args.log)
    logger.info("=" * 60)
    logger.info("Document Watchdog starting")
    logger.info(f"Watching: {watch_dir}")
    logger.info(f"API: {args.api}")
    logger.info("=" * 60)

    # Initialize components
    ingestor = PrivateGPTIngestor(args.api)
    scorer = DocumentScorer()
    processed: Set[str] = set()

    # Add custom keywords
    if args.sensitivity_keywords:
        SENSITIVITY_KEYWORDS["custom"] = args.sensitivity_keywords

    # Check API health
    try:
        health = requests.get(f"{args.api}/health", timeout=5)
        if health.status_code == 200:
            logger.info("✅ PrivateGPT API is reachable")
        else:
            logger.warning("⚠️ PrivateGPT API returned non-200 status")
    except Exception as e:
        logger.warning(f"⚠️ Could not reach PrivateGPT API: {e}")
        logger.warning("Watchdog will retry on each file.")

    # Set up observer
    event_handler = IngestEventHandler(
        ingestor=ingestor,
        scorer=scorer,
        logger=logger,
        processed=processed,
        sensitivity_keywords=args.sensitivity_keywords,
    )

    observer = Observer()
    observer.schedule(event_handler, str(watch_dir), recursive=args.recursive)
    observer.start()

    logger.info("Watchdog running. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        observer.stop()

    observer.join()
    logger.info("Watchdog stopped.")


if __name__ == "__main__":
    main()
