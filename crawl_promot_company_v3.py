import asyncio
import re
import sys
from urllib.parse import urlparse, urljoin

from crawl4ai import AsyncWebCrawler

# Windows-only ESC support via msvcrt
try:
    import msvcrt  # type: ignore
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False


# ---------------- CONFIG ----------------
MAX_PAGES = 10               # how many internal pages to attempt
SHOW_RAW = False             # set True to include cleaned text at bottom
CLEANED_MAX_CHARS = 12000    # truncate cleaned text if SHOW_RAW=True
MAX_BULLETS = 8              # bullets per section


def esc_pressed() -> bool:
    """Return True if ESC key was pressed (Windows console)."""
    if not HAS_MSVCRT:
        return False
    if msvcrt.kbhit():
        ch = msvcrt.getch()
        return ch == b"\x1b"  # ESC
    return False


def normalize_url(u: str) -> str:
    u = u.strip()
    if not u:
        return ""
    if not re.match(r"^https?://", u, flags=re.IGNORECASE):
        u = "https://" + u
    p = urlparse(u)
    if not p.netloc:
        raise ValueError(f"Invalid URL: {u}")
    return u


def same_domain(a: str, b: str) -> bool:
    return urlparse(a).netloc.lower() == urlparse(b).netloc.lower()


def host(url: str) -> str:
    return urlparse(url).netloc


def is_link_soup(line: str) -> bool:
    links = len(re.findall(r"\[[^\]]+\]\([^)]+\)", line))
    images = len(re.findall(r"!\[[^\]]*\]\([^)]+\)", line))
    return (links + images) >= 4


def is_mostly_media(line: str) -> bool:
    s = line.strip()
    if not s:
        return True
    if re.fullmatch(r"(!\[[^\]]*\]\([^)]+\)\s*)+", s):
        return True
    if len(re.findall(r"https?://", s)) >= 2 and len(s) < 180:
        return True
    return False


def looks_like_ui_chrome(line: str) -> bool:
    s = line.strip().lower()
    bad = [
        "request demo", "log in", "sign in", "menu", "back to top",
        "privacy policy", "terms", "cookie", "status", "careers",
        "thanks!", "oops! something went wrong", "all rights reserved",
        "© copyright", "copyright", "get started", "speak with an expert"
    ]
    if any(b in s for b in bad):
        return True
    if len(s) <= 28 and (s.startswith("[") or s.startswith("![")):
        return True
    return False


def clean_markdown(md: str) -> str:
    md = md.replace("\r\n", "\n")
    lines = [ln.rstrip() for ln in md.splitlines()]

    cleaned = []
    last = None

    for ln in lines:
        s = ln.strip()

        if not s:
            if cleaned and cleaned[-1] != "":
                cleaned.append("")
            continue

        if looks_like_ui_chrome(s):
            continue
        if is_mostly_media(s):
            continue
        if is_link_soup(s):
            continue

        # remove repeats
        if last is not None and s == last:
            continue
        last = s

        cleaned.append(s)

    out = "\n".join(cleaned)
    out = re.sub(r"\n{3,}", "\n\n", out).strip()
    return out


def markdown_to_text(md: str) -> str:
    # [Text](url) -> Text
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)
    # remove images
    t = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def split_sentences(text: str) -> list[str]:
    # simple, robust-enough sentence splitter
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text)
    out = []
    for p in parts:
        p = p.strip()
        if 40 <= len(p) <= 360:
            out.append(p)
    return out


def take_unique(items: list[str], limit: int) -> list[str]:
    seen = set()
    out = []
    for it in items:
        key = re.sub(r"\s+", " ", it.strip().lower())
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(it.strip())
        if len(out) >= limit:
            break
    return out


def best_company_name(clean_md: str, base_url: str) -> str:
    # Prefer legal entity from text (common on footers / press pages)
    t = markdown_to_text(clean_md)

    # Try “Inc”, “Ltd”, “LLC”, etc.
    m = re.search(r"\b([A-Z][A-Za-z0-9&.,' -]{2,60}\b(?:Inc\.?|LLC|Ltd\.?|Limited|GmbH|S\.A\.|S\.r\.l\.|AG))\b", t)
    if m:
        return m.group(1).strip()

    # Try first H1
    for line in clean_md.splitlines():
        if line.startswith("# "):
            cand = line[2:].strip()
            if 2 <= len(cand) <= 80:
                return cand

    return host(base_url)


def pick_bullets(clean_md: str, keyword_patterns: list[str], limit: int = MAX_BULLETS) -> list[str]:
    t = markdown_to_text(clean_md)
    sentences = split_sentences(t)

    hits = []
    for s in sentences:
        for pat in keyword_patterns:
            if re.search(pat, s, flags=re.IGNORECASE):
                hits.append(s)
                break

    return take_unique(hits, limit)


def md_bullets(items: list[str]) -> str:
    if not items:
        return "- *(not found in crawled pages)*"
    return "\n".join(f"- {x}" for x in items)


async def crawl_page(crawler: AsyncWebCrawler, url: str) -> str:
    result = await crawler.arun(url)
    return (result.markdown or "").strip()


def candidate_paths(base_url: str) -> list[str]:
    # High-signal pages for “people / funding / products”
    paths = [
        "/", "/about", "/about-us", "/company", "/team", "/leadership",
        "/news", "/newsroom", "/press", "/press-releases",
        "/blog", "/security",
        "/pricing",
        "/products", "/product", "/solutions",
        "/payouts", "/deposits", "/verification", "/stablecoin-settlement",
        "/api", "/docs"
    ]
    out = []
    for p in paths:
        out.append(urljoin(base_url, p))
    # de-dup while preserving order
    seen = set()
    final = []
    for u in out:
        if u not in seen:
            seen.add(u)
            final.append(u)
    return final


def build_report(base_url: str, merged_clean_md: str) -> str:
    company = best_company_name(merged_clean_md, base_url)

    sector = pick_bullets(merged_clean_md, [
        r"\bpayments?\b", r"\bfintech\b", r"\bsettlement\b", r"\bstablecoin\b",
        r"\bon-?ramp\b", r"\boff-?ramp\b", r"\bwallets?\b", r"\bexchanges?\b",
        r"\binfrastructure\b", r"\bplatform\b", r"\bapi\b"
    ])

    products = pick_bullets(merged_clean_md, [
        r"\bproduct(s)?\b", r"\bsolution(s)?\b", r"\bplatform\b", r"\bapi\b",
        r"\bverification\b", r"\bpayouts?\b", r"\bdeposits?\b",
        r"\bstablecoin settlement\b", r"\bon-?ramp\b", r"\boff-?ramp\b"
    ])

    competition = pick_bullets(merged_clean_md, [
        r"\bcompetitor(s)?\b", r"\bcompetition\b", r"\balternative(s)?\b",
        r"\bvs\.?\b", r"\bcompare\b"
    ])

    deals = pick_bullets(merged_clean_md, [
        r"\bpartner(s|ships)?\b", r"\btrusted by\b", r"\bcustomer(s)?\b",
        r"\bintegration(s)?\b", r"\bmeta(mask)?\b", r"\bcoinbase\b",
        r"\brevolut\b", r"\bfeatured in\b"
    ])

    technologies = pick_bullets(merged_clean_md, [
        r"\bapi\b", r"\bdeveloper(s)?\b", r"\bintegration\b",
        r"\bsecurity\b", r"\bcompliance\b", r"\bkyc\b", r"\baml\b",
        r"\bstablecoin(s)?\b", r"\bchain(s)?\b", r"\bwallet(s)?\b"
    ])

    key_people = pick_bullets(merged_clean_md, [
        r"\bfounded by\b", r"\bfounder(s)?\b", r"\bceo\b", r"\bcto\b", r"\bcfo\b",
        r"\bcoo\b", r"\bpresident\b", r"\bleadership\b", r"\bteam\b", r"\bboard\b"
    ])

    funding = pick_bullets(merged_clean_md, [
        r"\bfunding\b", r"\brais(ed|e)\b", r"\bseed\b", r"\bseries\s+[a-e]\b",
        r"\bvaluation\b", r"\bfinancing\b", r"\binvest(or|ors)\b"
    ])

    report = f"""# Company / Website Intelligence Report

**Source URL:** {base_url}

## Company name
- **{company}**

## Sector
{md_bullets(sector)}

## Products
{md_bullets(products)}

## Competition
{md_bullets(competition)}

## Deals
{md_bullets(deals)}

## Technologies
{md_bullets(technologies)}

## Key people
{md_bullets(key_people)}

## Funding rounds
{md_bullets(funding)}
"""

    if SHOW_RAW:
        text = merged_clean_md
        if len(text) > CLEANED_MAX_CHARS:
            text = text[:CLEANED_MAX_CHARS] + "\n\n... (truncated) ..."
        report += f"\n---\n\n## Cleaned merged content\n{text}\n"

    return report


async def main():
    print('Enter website URL(s) to crawl (comma-separated).')
    print('Press ESC anytime to stop.\n')

    raw = input("URL(s): ").strip()
    if not raw:
        print("No URL provided. Exiting.")
        return

    urls: list[str] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            urls.append(normalize_url(part))
        except ValueError as e:
            print(f"[SKIP] {e}")

    if not urls:
        print("No valid URLs. Exiting.")
        return

    print("\nStarting crawl... (press ESC to interrupt)\n")

    for idx, base_url in enumerate(urls, start=1):
        if esc_pressed():
            print("\n[INTERRUPT] ESC pressed. Stopping.")
            return

        print(f"[{idx}/{len(urls)}] Base: {base_url}")
        pages = candidate_paths(base_url)[:MAX_PAGES]

        merged_clean_parts = []
        visited = 0

        async with AsyncWebCrawler() as crawler:
            for p in pages:
                if esc_pressed():
                    print("\n[INTERRUPT] ESC pressed. Stopping.")
                    return

                try:
                    print(f"  - Crawling: {p}")
                    md = await crawl_page(crawler, p)
                    if not md:
                        continue

                    clean
