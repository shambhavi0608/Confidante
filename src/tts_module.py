"""Translation and text-to-speech services for generated sentences."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Dict, Tuple

LOGGER = logging.getLogger(__name__)


class TextToSpeechError(RuntimeError):
    """Raised when translation or speech synthesis fails."""


class TextToSpeechService:
    """Translate English text to Hindi and synthesize speech with emotion pacing."""

    def __init__(self) -> None:
        """Create a TTS service with speed mappings for supported emotions."""
        self.speed_by_emotion: Dict[str, bool] = {
            "neutral": False,
            "calm": True,
            "happy": False,
            "sad": True,
            "angry": False,
            "fearful": True,
            "disgust": False,
        }

    def translate(self, text: str, destination_language: str = "hi") -> str:
        """Translate text from English to the requested destination language."""
        cleaned = text.strip()
        if not cleaned:
            return ""
        if destination_language == "en":
            return cleaned
        try:
            from googletrans import Translator

            translator = Translator()
            result = translator.translate(cleaned, src="en", dest=destination_language)
            return str(result.text)
        except Exception as exc:
            LOGGER.warning("Translation failed; returning source text: %s", exc)
            return cleaned

    def synthesize(
        self,
        text: str,
        emotion: str = "neutral",
        language: str = "en",
        output_dir: str | Path | None = None,
    ) -> Tuple[Path, str]:
        """Create an MP3 file with gTTS and return its path plus spoken text."""
        spoken_text = self.translate(text, language)
        if not spoken_text:
            raise TextToSpeechError("Cannot synthesize empty text.")
        directory = Path(output_dir) if output_dir is not None else Path(tempfile.gettempdir())
        directory.mkdir(parents=True, exist_ok=True)
        output_path = directory / "sign_speech_output.mp3"
        try:
            from gtts import gTTS

            slow = self.speed_by_emotion.get(emotion, False)
            tts = gTTS(text=spoken_text, lang=language, slow=slow)
            tts.save(str(output_path))
            return output_path, spoken_text
        except Exception as exc:
            LOGGER.exception("Speech synthesis failed: %s", exc)
            raise TextToSpeechError(str(exc)) from exc
