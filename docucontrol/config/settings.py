from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parents[2]


@dataclass(slots=True)
class Settings:
    appearance_mode: str = os.getenv("DOCUCONTROL_APPEARANCE_MODE", "dark")
    color_theme: str = os.getenv("DOCUCONTROL_COLOR_THEME", "blue")

    data_import_dir: Path = Path(os.getenv("DOCUCONTROL_DATA_DIR", BASE_DIR / "data" / "input"))
    output_dir: Path = Path(os.getenv("DOCUCONTROL_OUTPUT_DIR", BASE_DIR / "data" / "output"))
    tmp_dir: Path = Path(os.getenv("DOCUCONTROL_TMP_DIR", BASE_DIR / "data" / "tmp"))

    assets_dir: Path = Path(os.getenv("DOCUCONTROL_ASSETS_DIR", BASE_DIR / "assets"))
    images_dir: Path = assets_dir / "images"
    templates_dir: Path = assets_dir / "templates"

    monitoring_report_name: str = os.getenv("DOCUCONTROL_MONITORING_NAME", "monitoring_report_{date}.xlsx")
    copy_prompt_enabled: bool = os.getenv("DOCUCONTROL_COPY_PROMPT", "true").lower() == "true"

    returns_base_dir: Path = Path(os.getenv("DOCUCONTROL_RETURNS_DIR", BASE_DIR / "data" / "returns"))
    tr_returns_dir: Path = returns_base_dir / "TECNICAS REUNIDAS"
    gaia_returns_dir: Path = returns_base_dir / "GAIA"
    prodoc_returns_dir: Path = returns_base_dir / "PRODOC"


settings = Settings()
 