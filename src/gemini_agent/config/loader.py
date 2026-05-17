"""YAML configuration loader for Gemini ADK agent framework."""

from pathlib import Path
import yaml

from .types import ConfigMap, ConfigValue


class ConfigLoadError(RuntimeError):
    """Raised when configuration files cannot be loaded."""


class ConfigLoader:
    """Load framework configuration files from a config root directory."""

    def __init__(self, config_root: Path) -> None:
        """Initialize loader with config root path."""
        self.config_root = config_root

    def load_all(self, *, environment: str) -> ConfigMap:
        """Load all mandatory configuration files for one environment."""
        return {
            "model_profiles": self.load_model_profiles(),
            "knowledge_sources": self.load_knowledge_sources(),
            "agent_catalog": self.load_agent_catalog(),
            "agents": self.load_agents(),
            "environment": self.load_environment(environment),
        }

    def load_model_profiles(self) -> ConfigMap:
        """Load model profile definitions."""
        return self._load_yaml(self.config_root / "model_profiles.yaml")

    def load_knowledge_sources(self) -> ConfigMap:
        """Load knowledge source definitions."""
        return self._load_yaml(self.config_root / "knowledge_sources.yaml")

    def load_agent_catalog(self) -> ConfigMap:
        """Load agent catalog definition."""
        return self._load_yaml(self.config_root / "agent_catalog.yaml")

    def load_agents(self) -> ConfigMap:
        """Load all per-agent config files under agents directory."""
        agents_dir = self.config_root / "agents"
        if not agents_dir.exists():
            msg = f"Missing config directory: {agents_dir}"
            raise ConfigLoadError(msg)
        if not agents_dir.is_dir():
            msg = f"Expected directory but found file: {agents_dir}"
            raise ConfigLoadError(msg)

        loaded: ConfigMap = {}
        for file_path in sorted(agents_dir.glob("*.yaml")):
            loaded[file_path.stem] = self._load_yaml(file_path)
        return loaded

    def load_environment(self, environment: str) -> ConfigMap:
        """Load one environment override file."""
        env_file = self.config_root / "environments" / f"{environment}.yaml"
        return self._load_yaml(env_file)

    def _load_yaml(self, file_path: Path) -> ConfigMap:
        """Load one YAML file and validate top-level type."""
        if not file_path.exists():
            msg = f"Missing config file: {file_path}"
            raise ConfigLoadError(msg)

        try:
            raw_data: object = yaml.safe_load(file_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            msg = f"Failed to parse YAML file {file_path}: {exc}"
            raise ConfigLoadError(msg) from exc

        if raw_data is None:
            return {}
        if not isinstance(raw_data, dict):
            msg = f"Top-level YAML document must be a mapping in file: {file_path}"
            raise ConfigLoadError(msg)
        try:
            return _validate_config_map(raw_data)
        except (TypeError, ValueError) as exc:
            msg = f"Invalid config mapping in file {file_path}: {exc}"
            raise ConfigLoadError(msg) from exc


def _validate_config_map(data: dict[object, object]) -> ConfigMap:
    validated: ConfigMap = {}
    for key, value in data.items():
        if not isinstance(key, str):
            msg = "Top-level YAML mapping keys must be strings."
            raise TypeError(msg)
        validated[key] = _validate_config_value(value)
    return validated


def _validate_config_value(value: object) -> ConfigValue:
    if isinstance(value, dict):
        return _validate_config_map(value)
    if isinstance(value, list):
        return [_validate_config_value(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    msg = f"Unsupported config value type: {type(value).__name__}"
    raise ValueError(msg)
