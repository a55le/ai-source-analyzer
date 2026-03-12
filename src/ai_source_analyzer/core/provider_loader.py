import importlib.util
import inspect
import pkgutil

from ai_source_analyzer.providers.base import BaseProvider
from ai_source_analyzer.core.providers_registry import ProvidersRegistry
from ai_source_analyzer.config import settings
from ai_source_analyzer.core.logger import logger
import ai_source_analyzer.providers as providers_package

def _missing_env_keys(required_env: list[str]) -> list[str]:
    missing: list[str] = []
    
    for key in required_env:
        value = settings.model_dump().get(key)
        
        if value is None:
            missing.append(key)
            
    return missing
    
def load_providers(
    registry: ProvidersRegistry
):
    loaded: list[str] = []
    package_name = providers_package.__name__
    
    for module_info in pkgutil.iter_modules(providers_package.__path__):
        module_name = module_info.name
        
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
            missing = _missing_env_keys(getattr(cls, "required_env", []) or [])
        
            if missing:
                logger.warn(
                    f"Provider '{provider_name}' skipped: missing env keys: {', '.join(missing)}"
                )
                
                continue
        
            instance = cls()
            registry.register(instance)
            loaded.append(instance.name)
    
    return loaded