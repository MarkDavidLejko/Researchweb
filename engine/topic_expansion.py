import random


def expand_topic(topic: str) -> list[str]:
    """Generiert 5 Unterthemen basierend auf einfachem Dummy-Heuristik-Ansatz."""
    subtopics = [f"{topic} – Aspekt {i}" for i in range(1, 6)]
    random.shuffle(subtopics)  # sorgt für Variation
    return subtopics


def get_short_description(topic: str) -> str:
    """Erzeugt eine kurze (max. 200 Zeichen) Beschreibung."""
    return (f"{topic} ist ein interessantes Gebiet. "
            "Hier lassen sich vielfältige Zusammenhänge und Teilbereiche entdecken.")[:200]
