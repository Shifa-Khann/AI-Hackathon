"""Topic taxonomy shared by onboarding chips, tagger, scorer and learner."""
from __future__ import annotations

# id, label, keywords (lower-case) used by the offline tagger / profiler
_RAW = [
    ("ai", "Artificial intelligence", "ai artificial intelligence llm model chatbot machine learning neural openai anthropic"),
    ("software", "Software & dev", "software developer programming code open source rust python framework api compiler"),
    ("cybersecurity", "Cybersecurity", "security breach hack vulnerability ransomware malware encryption phishing"),
    ("startups", "Startups & venture", "startup founder venture funding seed round unicorn accelerator"),
    ("markets", "Markets & investing", "stocks shares index equity bond investor psx earnings rally selloff"),
    ("economy_pk", "Pakistan economy", "pakistan rupee sbp inflation imf budget exports remittances tax"),
    ("business", "Business", "company merger acquisition retail supply chain ceo profits industry"),
    ("energy", "Energy", "energy oil gas solar power grid electricity opec refinery"),
    ("climate", "Climate", "climate emissions warming flood heatwave carbon biodiversity"),
    ("politics_pk", "Pakistan politics", "pakistan parliament senate election national assembly provincial minister court"),
    ("geopolitics", "World affairs", "treaty summit diplomacy ceasefire sanctions border alliance united nations"),
    ("cricket", "Cricket", "cricket test odi t20 batter bowler wicket pcb innings series"),
    ("football", "Football", "football league goal striker club transfer premier"),
    ("f1", "Formula 1", "formula f1 grand prix driver qualifying constructor pit"),
    ("health", "Health", "health hospital vaccine disease nutrition clinical patients"),
    ("science", "Science", "science researchers study physics biology experiment discovery"),
    ("space", "Space", "space nasa rocket orbit satellite lunar mars telescope"),
    ("education", "Education", "education university students school exam curriculum scholarship"),
    ("design", "Design & UX", "design ux typography interface designer prototype accessibility"),
    ("books", "Books & ideas", "book novel author essay literature publisher"),
    ("film_music", "Film & music", "film cinema album concert streaming series director soundtrack"),
    ("culture", "Culture & society", "culture festival heritage society city community tradition"),
    ("travel", "Travel", "travel tourism flights airline destination trek"),
    ("crypto", "Crypto & fintech", "crypto bitcoin blockchain fintech payments wallet stablecoin"),
]

TOPICS: list[dict] = [
    {"id": i, "label": l, "keywords": k.split()} for i, l, k in _RAW
]
TOPIC_IDS = [t["id"] for t in TOPICS]
LABELS = {t["id"]: t["label"] for t in TOPICS}


def label(topic_id: str) -> str:
    return LABELS.get(topic_id, topic_id.replace("_", " ").title())


def public_topics() -> list[dict]:
    return [{"id": t["id"], "label": t["label"]} for t in TOPICS]
