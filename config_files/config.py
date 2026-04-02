from config_schema import DatabaseConfig, SettingsConfig, AppConfig

db_config = DatabaseConfig(
    db_name="postgres",
    db_port=5432,
    db_user="admin",
    db_password="secret",
    db_departments=["Finance", "HR"]
)

settings_config = SettingsConfig(
    debug=True,
    timeout=30
)

config = AppConfig(
    database=db_config,
    settings=settings_config
)
