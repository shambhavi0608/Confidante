"""Prediction smoothing with a majority vote buffer and cooldown window."""

from __future__ import annotations

import time
from collections import Counter, deque
from dataclasses import dataclass, field
from typing import Deque, Optional, Tuple


@dataclass
class MajorityVoteSmoother:
    """Smooth frame-level gesture predictions before committing text tokens."""

    buffer_size: int = 7
    cooldown_seconds: float = 1.5
    confidence_threshold: float = 0.75
    _buffer: Deque[Tuple[str, float]] = field(init=False)
    _last_emit_time: float = field(default=0.0, init=False)
    _last_emit_label: Optional[str] = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Initialize the fixed-size prediction buffer."""
        self._buffer = deque(maxlen=max(1, self.buffer_size))

    def update_settings(
        self,
        buffer_size: Optional[int] = None,
        cooldown_seconds: Optional[float] = None,
        confidence_threshold: Optional[float] = None,
    ) -> None:
        """Update smoothing settings while preserving recent compatible predictions."""
        if buffer_size is not None and buffer_size != self.buffer_size:
            self.buffer_size = max(1, int(buffer_size))
            self._buffer = deque(list(self._buffer)[-self.buffer_size :], maxlen=self.buffer_size)
        if cooldown_seconds is not None:
            self.cooldown_seconds = max(0.0, float(cooldown_seconds))
        if confidence_threshold is not None:
            self.confidence_threshold = min(1.0, max(0.0, float(confidence_threshold)))

    def add(self, label: str, confidence: float, timestamp: Optional[float] = None) -> Optional[str]:
        """Add a prediction and return a stable label when it passes all gates."""
        now = timestamp if timestamp is not None else time.time()
        if confidence < self.confidence_threshold:
            return None
        self._buffer.append((label, confidence))
        if len(self._buffer) < self.buffer_size:
            return None
        labels = [item[0] for item in self._buffer]
        majority_label, majority_count = Counter(labels).most_common(1)[0]
        if majority_count <= self.buffer_size // 2:
            return None
        if majority_label == "NOTHING":
            return None
        if self._last_emit_label == majority_label and now - self._last_emit_time < self.cooldown_seconds:
            return None
        self._last_emit_label = majority_label
        self._last_emit_time = now
        return majority_label

    def reset(self) -> None:
        """Clear buffered predictions and cooldown state."""
        self._buffer.clear()
        self._last_emit_time = 0.0
        self._last_emit_label = None
