from pydantic import BaseModel
from typing import Optional

class DatabaseConfig(BaseModel):
    db_name: str
    db_port: int
    db_user: str
    db_password: str
    db_departments: list

class SettingsConfig(BaseModel):
    debug: Optional[bool] = False
    timeout: int

class AppConfig(BaseModel):
    database: DatabaseConfig
    settings: SettingsConfig
