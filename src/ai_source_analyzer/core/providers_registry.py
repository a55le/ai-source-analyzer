from ai_source_analyzer.providers.base import BaseProvider


class ProvidersRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, BaseProvider] = {}
        
    def register(self, provider: BaseProvider) -> None:
        if not provider.name:
            raise ValueError("Provider must have a non-empty name")
        
        self._providers[provider.name] = provider
        
    def get(self, name: str) -> BaseProvider:
        try:
            return self._providers[name]
        except KeyError as e:
            available = ", ".join(self._providers.keys()) or "none"
            
            raise KeyError(
                f"Provider '{name}' not found. Available providers: {available}"
            ) from e
    
    def get_many(self, names: list[str]) -> list[BaseProvider]:
        return [self.get(name) for name in names]
        
    def list_names(self) -> list[str]:
        return sorted(self._providers.keys())

    def all(self) -> list[BaseProvider]:
        return [self._providers[name] for name in self._providers]