from pathlib import Path

from platformdirs import user_config_dir

config_dir = Path(user_config_dir("pytodo", "FrancyAngy"))
config_dir.mkdir(parents=True, exist_ok=True)

db_path = config_dir / "todo.db"

db_url = f"sqlite://{db_path.as_posix()}"
