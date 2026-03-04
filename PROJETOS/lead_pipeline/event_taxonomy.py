from __future__ import annotations

from .normalization import city_key


EVENT_TYPE_TAXONOMY = {
    "VERT BATTLE :: NITERÓI": "ESPORTE | SKATE | VERTICAL",
    "VERT BATTLE :: GOIÂNIA": "ESPORTE | SKATE | VERTICAL",
    "Circuito Banco do Brasil de Corridas": "ESPORTE | CORRIDA DE RUA",
    "Park Challenge 2025": "ESPORTE | SKATE | STREET",
    "SLS Select Series Brasília 2025": "ESPORTE | SKATE | STREET",
    "SLS Super Crown 2025": "ESPORTE | SKATE | STREET",
    "SLS Select Series Florianópolis 2025": "ESPORTE | SKATE | STREET",
    "SLS Select Series Saquarema 2025": "ESPORTE | SKATE | STREET",
}

_EVENT_TYPE_BY_KEY = {
    city_key(event_name): event_type
    for event_name, event_type in EVENT_TYPE_TAXONOMY.items()
}
BATUKE_EVENT_PREFIX = city_key("Batuke do Pretinho")


def classify_event_type(event_name: str) -> str | None:
    key = city_key(event_name)
    if not key:
        return None
    if key.startswith(BATUKE_EVENT_PREFIX):
        return "Show"
    return _EVENT_TYPE_BY_KEY.get(key)
