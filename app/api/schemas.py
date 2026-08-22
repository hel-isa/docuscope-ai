from __future__ import annotations

from pydantic import BaseModel


class ScanRequest(BaseModel):
    input_folder: str
    sqlite: bool = False
