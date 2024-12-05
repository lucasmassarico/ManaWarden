import os
import logging
from datetime import datetime
import ast


class LogManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, log_file="../application.log"):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True

        self.logger = logging.getLogger("AppLogger")
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # File Handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def log(self, level, message):
        if level == "info":
            self.logger.info(message)
        elif level == "debug":
            self.logger.debug(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "warning":
            self.logger.warning(message)


class ConfigManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, config_path="../configs.mana"):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True

        self.logger = LogManager()
        self.config_path = config_path
        self.config_data = {}
        self.observers = {}
        self._load_configs()

    def _load_configs(self):
        """Load configs on file"""
        if not os.path.exists(self.config_path):
            self.logger.log("warning", f"Config file not found: {self.config_path}")
            return

        try:
            with open(self.config_path, "r") as file:
                for line in file:
                    stripped_line = line.strip()
                    if not stripped_line or stripped_line.startswith("#"):
                        continue
                    if "=" in stripped_line:
                        key, value = stripped_line.split("=", 1)
                        key = key.strip()
                        value = value.strip()

                        if not value:
                            self.config_data[key] = None
                        else:
                            try:
                                self.config_data[key.strip()] = ast.literal_eval(value.strip())
                            except ValueError as e:
                                self.logger.log("error", f"Failed to parse value for {key.strip()}: {e}")
                                self.config_data[key.strip()] = None
        except Exception as e:
            self.logger.log("error", f"Failed to load configuration: {e}")

    def get(self, key, default=None):
        """Get config by name, returning default value if not found."""
        value = self.config_data.get(key, default)
        if value is default:
            self.logger.log("info", f"Config key '{key}' not found. Returning default: {default}")
        return value

    def set(self, key, value):
        """Set a configuration key and value."""
        self.config_data[key] = value
        self.save_config()
        self._notify_observers(key)

    def save_config(self):
        """Save configurations back to the file."""
        try:
            with open(self.config_path, "w") as file:
                for key, value in self.config_data.items():
                    file.write(f"{key}={repr(value)}\n")
            self.logger.log("info", f"Configuration saved to {self.config_path}")
        except Exception as e:
            self.logger.log("error", f"failed to save configuration: {e}")

    def add_observer(self, key, observer):
        """add one observer to specific config."""
        if key not in self.observers:
            self.observers[key] = []
        self.observers[key].append(observer)

    def _notify_observers(self, key):
        """Notify all observers registered to key."""
        if key in self.observers:
            for observer in self.observers[key]:
                observer.on_config_update(key, self.config_data[key])

    def validate_config(self, required_keys):
        """Validate if all required keys exist and have valid values."""
        missing_keys = [key for key in required_keys if key not in self.config_data]
        if missing_keys:
            self.logger.log("error", f"Missing required configuration keys: {missing_keys}")
            raise ValueError(f"Missing required keys: {missing_keys}")

        # Validar os valores (exemplo: tipo e formato)
        for key in required_keys:
            value = self.config_data.get(key)
            if key.endswith("_region") and not isinstance(value, list):
                self.logger.log("error", f"Invalid value for key '{key}': Expected a list, got {type(value).__name__}")
                raise ValueError(f"Invalid value for key '{key}': {value}")

    def reset_config(self):
        """Reset configurations to an empty state."""
        self.config_data.clear()
        self.logger.log("info", "Configurations reset to default (empty state).")


# config = ConfigManager()
# print(config.config_data)
