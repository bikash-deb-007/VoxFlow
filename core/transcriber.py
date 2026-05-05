import numpy as np
import whisper


class Transcriber:
    def __init__(self, model_name: str = "base", language: str | None = None):
        self.model_name = model_name
        self.language = language
        self._model: whisper.Whisper | None = None

    def load(self) -> None:
        self._model = whisper.load_model(self.model_name)

    def reload(self, model_name: str, language: str | None) -> None:
        self.model_name = model_name
        self.language = language
        self._model = whisper.load_model(model_name)

    def transcribe(self, audio: np.ndarray) -> tuple[str, str]:
        if self._model is None:
            raise RuntimeError("Model not loaded. Call load() first.")
        result = self._model.transcribe(
            audio,
            language=self.language,
            fp16=False,
        )
        text = result["text"].strip()
        lang = result.get("language", "?")
        return text, lang
