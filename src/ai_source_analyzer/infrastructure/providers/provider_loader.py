import importlib
import inspect
import pkgutil

import ai_source_analyzer.infrastructure.providers as providers_package
from ai_source_analyzer.application.ports.logger import LoggerPort
from ai_source_analyzer.infrastructure.config.settings import Settings
from ai_source_analyzer.infrastructure.providers.base import BaseProvider
from ai_source_analyzer.infrastructure.providers.providers_registry import (
    ProvidersRegistry,
)


def _missing_env_keys(settings: Settings, required_env: list[str]) -> list[str]:
    values = settings.model_dump()
    return [key for key in required_env if values.get(key) is None]


def load_providers(
    registry: ProvidersRegistry,
    settings: Settings,
    logger: LoggerPort,
) -> list[str]:
    loaded: list[str] = []
    package_name = providers_package.__name__
    internal_modules = {"base", "provider_loader", "providers_registry"}

    for module_info in pkgutil.iter_modules(providers_package.__path__):
        module_name = module_info.name
        if module_name in internal_modules:
            continue

        full_module_name = f"{package_name}.{module_name}"
        module = importlib.import_module(full_module_name)

        for _, cls in inspect.getmembers(module, inspect.isclass):
            if cls is BaseProvider:
                continue
            if cls.__module__ != full_module_name:
                continue
            if not issubclass(cls, BaseProvider):
                continue

            provider_name = getattr(cls, "name", cls.__name__)
            missing = _missing_env_keys(
                settings=settings,
                required_env=getattr(cls, "required_env", []) or [],
            )
            if missing:
                logger.warn(
                    f"Provider '{provider_name}' skipped: missing env keys: {', '.join(missing)}"
                )
                continue

            instance = cls()
            registry.register(instance)
            loaded.append(instance.name)

    return loaded
