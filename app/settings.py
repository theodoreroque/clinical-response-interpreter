import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    model_source: str = "package"
    model_path: str | None = None
    model_package: str = "en_yes_no_detection"
    clarification_threshold: float = 0.70
    model_version: str = "unknown"


def get_settings() -> Settings:
    return Settings(
        model_source=os.getenv("MODEL_SOURCE", "package").lower(),
        model_path=os.getenv("MODEL_PATH"),
        model_package=os.getenv("MODEL_PACKAGE", "en_yes_no_detection"),
        clarification_threshold=float(os.getenv("CLARIFICATION_THRESHOLD", "0.70")),
        model_version=os.getenv("MODEL_VERSION", "unknown"),
    )

