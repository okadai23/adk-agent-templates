"""YAML configuration loader for Gemini ADK agent framework."""

from pathlib import Path
from collections.abc import Mapping

from pydantic import TypeAdapter, ValidationError
import yaml

from .types import ConfigMap


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
        if not isinstance(raw_data, Mapping):
            msg = f"Top-level YAML document must be a mapping in file: {file_path}"
            raise ConfigLoadError(msg)
        try:
            return self._config_map_adapter.validate_python(raw_data)
        except ValidationError as exc:
            msg = f"Invalid config mapping in file {file_path}: {exc}"
            raise ConfigLoadError(msg) from exc
    _config_map_adapter = TypeAdapter(ConfigMap)
