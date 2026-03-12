from ai_source_analyzer.application.ports.provider import ProviderPort


class ProvidersRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, ProviderPort] = {}

    def register(self, provider: ProviderPort) -> None:
        if not provider.name:
            raise ValueError("Provider must have a non-empty name")
        self._providers[provider.name] = provider

    def get(self, name: str) -> ProviderPort:
        try:
            return self._providers[name]
        except KeyError as error:
            available = ", ".join(self._providers.keys()) or "none"
            raise KeyError(
                f"Provider '{name}' not found. Available providers: {available}"
            ) from error

    def get_many(self, names: list[str]) -> list[ProviderPort]:
        return [self.get(name) for name in names]

    def list_names(self) -> list[str]:
        return sorted(self._providers.keys())

    def all(self) -> list[ProviderPort]:
        return [self._providers[name] for name in self._providers]
