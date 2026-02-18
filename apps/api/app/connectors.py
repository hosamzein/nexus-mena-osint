from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha1
from typing import Dict, List

from .schemas import ConnectorStatus, ContentItem, Platform, SourceCatalogEntry


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

CONNECTOR_HEALTH = [
    ConnectorStatus(
        connector="sherlock-identity",
        domain="social_identity",
        health="healthy",
        success_rate=0.98,
        avg_latency_ms=420,
    ),
    ConnectorStatus(
        connector="telegram-intel-pack",
        domain="social_content",
        health="healthy",
        success_rate=0.95,
        avg_latency_ms=510,
    ),
    ConnectorStatus(
        connector="instagram-intel-pack",
        domain="social_content",
        health="degraded",
        success_rate=0.88,
        avg_latency_ms=860,
        last_error="rate-limit burst in last run",
    ),
    ConnectorStatus(
        connector="web-check-stack",
        domain="web_infra",
        health="healthy",
        success_rate=0.99,
        avg_latency_ms=310,
    ),
    ConnectorStatus(
        connector="theharvester-domain-enum",
        domain="web_infra",
        health="healthy",
        success_rate=0.93,
        avg_latency_ms=740,
    ),
]

SOURCE_CATALOG = [
    SourceCatalogEntry(
        id="src_awesome_osint",
        name="Awesome OSINT",
        category="catalog",
        source_type="index",
        origin_repo="jivoi/awesome-osint",
        url="https://github.com/jivoi/awesome-osint",
        tags=["catalog", "multi-domain", "discovery"],
    ),
    SourceCatalogEntry(
        id="src_spiderfoot",
        name="SpiderFoot",
        category="engine",
        source_type="tool",
        origin_repo="smicallef/spiderfoot",
        url="https://github.com/smicallef/spiderfoot",
        tags=["automation", "correlation", "osint"],
    ),
    SourceCatalogEntry(
        id="src_sherlock",
        name="Sherlock",
        category="identity",
        source_type="tool",
        origin_repo="sherlock-project/sherlock",
        url="https://github.com/sherlock-project/sherlock",
        tags=["username", "social", "discovery"],
    ),
    SourceCatalogEntry(
        id="src_social_analyzer",
        name="Social Analyzer",
        category="identity",
        source_type="tool",
        origin_repo="qeeqbox/social-analyzer",
        url="https://github.com/qeeqbox/social-analyzer",
        tags=["identity", "confidence", "social"],
    ),
    SourceCatalogEntry(
        id="src_web_check",
        name="Web Check",
        category="web_infra",
        source_type="tool",
        origin_repo="Lissy93/web-check",
        url="https://github.com/Lissy93/web-check",
        tags=["domain", "tls", "headers"],
    ),
    SourceCatalogEntry(
        id="src_telegram_osint",
        name="Telegram OSINT Toolbox",
        category="social_content",
        source_type="catalog",
        origin_repo="The-Osint-Toolbox/Telegram-OSINT",
        url="https://github.com/The-Osint-Toolbox/Telegram-OSINT",
        tags=["telegram", "channels", "groups"],
    ),
    SourceCatalogEntry(
        id="src_instagram_osint",
        name="Osintgram",
        category="social_content",
        source_type="tool",
        origin_repo="Datalux/Osintgram",
        url="https://github.com/Datalux/Osintgram",
        tags=["instagram", "posts", "metadata"],
    ),
]


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
        media_hash = None
        if platform in {Platform.instagram, Platform.telegram, Platform.youtube}:
            media_hash = sha1(f"media:{platform.value}:{i // 2}".encode("utf-8")).hexdigest()[:16]
        narrative_key = "energy-claims-wave" if "claims" in text.lower() else "coordinated-amplification"
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
                source_name=f"{platform.value}-collector",
                media_hash=media_hash,
                narrative_key=narrative_key,
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
        if item.narrative_key:
            narrative_node = f"narrative:{item.narrative_key}"
            nodes[narrative_node] = {
                "id": narrative_node,
                "label": item.narrative_key,
                "type": "narrative",
            }
            edges.append({"source": account_node, "target": narrative_node, "type": "amplifies"})
    return {"nodes": list(nodes.values()), "edges": edges}


def list_connector_health() -> List[ConnectorStatus]:
    return CONNECTOR_HEALTH


def list_source_catalog() -> List[SourceCatalogEntry]:
    return SOURCE_CATALOG
