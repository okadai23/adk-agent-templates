"""YAML configuration loader for Gemini ADK agent framework."""

from pathlib import Path
from collections.abc import Mapping

import yaml


class ConfigLoadError(RuntimeError):
    """Raised when configuration files cannot be loaded."""


class ConfigLoader:
    """Load framework configuration files from a config root directory."""

    def __init__(self, config_root: Path) -> None:
        """Initialize loader with config root path."""
        self.config_root = config_root

    def load_all(self, *, environment: str) -> dict[str, object]:
        """Load all mandatory configuration files for one environment."""
        return {
            "model_profiles": self.load_model_profiles(),
            "knowledge_sources": self.load_knowledge_sources(),
            "agent_catalog": self.load_agent_catalog(),
            "agents": self.load_agents(),
            "environment": self.load_environment(environment),
        }

    def load_model_profiles(self) -> dict[str, object]:
        """Load model profile definitions."""
        return self._load_yaml(self.config_root / "model_profiles.yaml")

    def load_knowledge_sources(self) -> dict[str, object]:
        """Load knowledge source definitions."""
        return self._load_yaml(self.config_root / "knowledge_sources.yaml")

    def load_agent_catalog(self) -> dict[str, object]:
        """Load agent catalog definition."""
        return self._load_yaml(self.config_root / "agent_catalog.yaml")

    def load_agents(self) -> dict[str, object]:
        """Load all per-agent config files under agents directory."""
        agents_dir = self.config_root / "agents"
        if not agents_dir.exists():
            msg = f"Missing config directory: {agents_dir}"
            raise ConfigLoadError(msg)
        if not agents_dir.is_dir():
            msg = f"Expected directory but found file: {agents_dir}"
            raise ConfigLoadError(msg)

        loaded: dict[str, object] = {}
        for file_path in sorted(agents_dir.glob("*.yaml")):
            loaded[file_path.stem] = self._load_yaml(file_path)
        return loaded

    def load_environment(self, environment: str) -> dict[str, object]:
        """Load one environment override file."""
        env_file = self.config_root / "environments" / f"{environment}.yaml"
        return self._load_yaml(env_file)

    def _load_yaml(self, file_path: Path) -> dict[str, object]:
        """Load one YAML file and validate top-level type."""
        if not file_path.exists():
            msg = f"Missing config file: {file_path}"
            raise ConfigLoadError(msg)

        try:
            raw_data = yaml.safe_load(file_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            msg = f"Failed to parse YAML file {file_path}: {exc}"
            raise ConfigLoadError(msg) from exc

        if raw_data is None:
            return {}
        if not isinstance(raw_data, Mapping):
            msg = f"Top-level YAML document must be a mapping in file: {file_path}"
            raise ConfigLoadError(msg)
        for key in raw_data:
            if not isinstance(key, str):
                msg = (
                    "Top-level YAML mapping keys must be strings in file: "
                    f"{file_path}"
                )
                raise ConfigLoadError(msg)
        return {str(key): value for key, value in raw_data.items()}
