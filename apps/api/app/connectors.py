from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha1
from typing import Dict, List

from .schemas import ContentItem, Platform


SEED_TEXT = {
    Platform.x: [
        "Breaking: circulating claims about policy changes with no cited source",
        "Coordinated repost wave detected around regional energy narrative",
        "Multiple accounts amplifying identical text in Arabic and English",
    ],
    Platform.telegram: [
        "Forwarded post with unverifiable casualty claims and viral traction",
        "Channel network shares mirrored narrative blocks within minutes",
        "Media asset reused with altered caption targeting local audience",
    ],
    Platform.youtube: [
        "Comment clusters repeating same claim template across videos",
        "Re-uploaded clip framed as current event without timestamp context",
        "Cross-linking to low-credibility domains in description threads",
    ],
    Platform.instagram: [
        "Carousel post spreads infographic with missing citation metadata",
        "Stories from multiple pages synchronize wording and hashtag sets",
        "Recycled image appears with contradictory location tagging",
    ],
    Platform.web: [
        "Blog network republishes the same article body with modified headlines",
        "Domain cluster shows coordinated backlinking to boost visibility",
        "Low-trust pages embed copied claims without source attribution",
    ],
}


def _entity_extract(text: str) -> List[str]:
    entities = []
    for token in text.replace(":", "").replace(",", "").split():
        if token.lower() in {"mena", "arabic", "english", "policy", "energy", "claims"}:
            entities.append(token.lower())
    return sorted(set(entities))


def collect_platform_items(case_id: str, query: str, platform: Platform, count: int = 4) -> List[ContentItem]:
    now = datetime.now(timezone.utc)
    source = SEED_TEXT[platform]
    items: List[ContentItem] = []
    for i in range(count):
        seed = source[i % len(source)]
        text = f"{seed} | query={query}"
        author = f"{platform.value}_account_{i + 1}"
        fingerprint = sha1(f"{case_id}:{platform.value}:{author}:{text}".encode("utf-8")).hexdigest()[:12]
        items.append(
            ContentItem(
                id=f"itm_{platform.value}_{fingerprint}",
                case_id=case_id,
                platform=platform,
                author=author,
                text=text,
                url=f"https://intel.local/{platform.value}/{fingerprint}",
                observed_at=now - timedelta(minutes=i * 3),
                language="ar" if i % 2 == 0 else "en",
                engagement=(i + 1) * 120,
                entities=_entity_extract(text),
            )
        )
    return items


def collect_case_items(case_id: str, query: str, platforms: List[Platform]) -> List[ContentItem]:
    items: List[ContentItem] = []
    for platform in platforms:
        items.extend(collect_platform_items(case_id, query, platform))
    return items


def build_case_graph(items: List[ContentItem]) -> Dict[str, List[Dict[str, str]]]:
    nodes: Dict[str, Dict[str, str]] = {}
    edges: List[Dict[str, str]] = []
    for item in items:
        account_node = f"acct:{item.author}"
        platform_node = f"platform:{item.platform.value}"
        nodes[account_node] = {"id": account_node, "label": item.author, "type": "account"}
        nodes[platform_node] = {"id": platform_node, "label": item.platform.value, "type": "platform"}
        edges.append({"source": account_node, "target": platform_node, "type": "posts_on"})
        for entity in item.entities:
            entity_node = f"entity:{entity}"
            nodes[entity_node] = {"id": entity_node, "label": entity, "type": "entity"}
            edges.append({"source": account_node, "target": entity_node, "type": "mentions"})
    return {"nodes": list(nodes.values()), "edges": edges}
