from dataclasses import dataclass
from fastapi import Form


@dataclass
class FieldSetupModel:
    name: str = Form()
    operation: str = Form()
