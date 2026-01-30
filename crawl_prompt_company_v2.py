import asyncio
import re
import sys
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler

# Windows-only ESC support via msvcrt
try:
    import msvcrt  # type: ignore
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False


# ---- CONFIG ----
SHOW_RAW = False          # set True if you want to print raw markdown at bottom
RAW_MAX_CHARS = 6000      # truncate raw markdown if SHOW_RAW=True
MAX_BULLETS = 8           # bullets per section


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


def esc_pressed() -> bool:
    """Return True if ESC key was pressed (Windows console)."""
    if not HAS_MSVCRT:
        return False
    if msvcrt.kbhit():
        ch = msvcrt.getch()
        return ch == b"\x1b"  # ESC
    return False


def find_first_h1(markdown: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def host_from_url(url: str) -> str:
    return urlparse(url).netloc


def is_link_soup(line: str) -> bool:
    """
    Detect nav/menu lines: lots of [text](link) in one line.
    """
    links = len(re.findall(r"\[[^\]]+\]\([^)]+\)", line))
    images = len(re.findall(r"!\[[^\]]*\]\([^)]+\)", line))
    # if a line has many links/images, it's usually navigation / footer
    return (links + images) >= 4


def is_mostly_media(line: str) -> bool:
    """
    Lines that are just images/icons/logos.
    """
    s = line.strip()
    if not s:
        return True
    # image-only or mostly URLs
    if re.fullmatch(r"(!\[[^\]]*\]\([^)]+\)\s*)+", s):
        return True
    if len(re.findall(r"https?://", s)) >= 2 and len(s) < 160:
        return True
    return False


def looks_like_ui_chrome(line: str) -> bool:
    """
    Remove common UI labels that pollute extraction.
    """
    s = line.strip().lower()
    bad_fragments = [
        "request demo", "log in", "sign in", "menu", "back to top",
        "privacy policy", "terms", "cookie", "status", "careers",
        "thanks!", "oops! something went wrong", "ok"
    ]
    if any(b in s for b in bad_fragments):
        return True
    # very short link-only lines
    if len(s) <= 24 and ("http" in s or s.startswith("[") or s.startswith("![")):
        return True
    return False


def clean_markdown(md: str) -> str:
    """
    Aggressive cleanup for homepages:
    - remove link-soup/nav lines
    - remove image-only lines
    - remove UI chrome lines
    - de-duplicate consecutive repeats
    """
    md = md.replace("\r\n", "\n")
    lines = [ln.rstrip() for ln in md.splitlines()]

    cleaned = []
    prev = None

    for ln in lines:
        s = ln.strip()

        # normalize whitespace-only lines
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

        # remove obvious repeated junk
        if prev is not None and s == prev:
            continue
        prev = s

        cleaned.append(s)

    # collapse many blank lines
    out = "\n".join(cleaned)
    out = re.sub(r"\n{3,}", "\n\n", out).strip()
    return out


def text_for_search(md: str) -> str:
    """
    Convert markdown to a more searchable plain-ish text:
    - keep headings
    - strip link targets, keep anchor text
    """
    # keep anchor text: [Text](url) -> Text
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)
    # drop images entirely: ![alt](url) -> ""
    t = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", t)
    # normalize spaces
    t = re.sub(r"\s+", " ", t).strip()
    return t


def take_unique(items: list[str], limit: int) -> list[str]:
    seen = set()
    out = []
    for it in items:
        it2 = it.strip()
        if not it2:
            continue
        key = it2.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(it2)
        if len(out) >= limit:
            break
    return out


def extract_bullets(md_clean: str, patterns: list[str], limit: int = MAX_BULLETS) -> list[str]:
    """
    Extract sentences/snippets around patterns, from cleaned content.
    """
    t = text_for_search(md_clean)

    snippets = []
    for pat in patterns:
        for m in re.finditer(pat, t, flags=re.IGNORECASE):
            start = max(0, m.start() - 160)
            end = min(len(t), m.end() + 220)
            snippet = t[start:end].strip()
            # tighten snippet
            snippet = re.sub(r"\s+", " ", snippet)
            if len(snippet) < 40:
                continue
            snippets.append(snippet)
            if len(snippets) >= limit * 3:
                break
        if len(snippets) >= limit * 3:
            break

    return take_unique(snippets, limit)


def md_bullets(items: list[str]) -> str:
    if not items:
        return "- *(not found on page)*"
    # trim overly long bullets
    out = []
    for s in items:
        s = s.strip()
        if len(s) > 320:
            s = s[:320].rstrip() + "…"
        out.append(f"- {s}")
    return "\n".join(out)


def build_report(url: str, raw_md: str) -> str:
    md_clean = clean_markdown(raw_md)

    # Company name: first H1 after cleaning, else domain
    company = find_first_h1(md_clean)
    if not company:
        company = host_from_url(url)

    # Patterns (tuned for company sites / startups)
    sector = extract_bullets(md_clean, [
        r"\bplatform\b", r"\binfrastructure\b", r"\bpayments?\b", r"\bfintech\b",
        r"\bsecurity\b", r"\bcompliance\b", r"\bsettlement\b", r"\bwallets?\b",
        r"\bexchange(s)?\b", r"\bapi(s)?\b", r"\bb2b\b", r"\benterprise\b"
    ])

    products = extract_bullets(md_clean, [
        r"\bproduct(s)?\b", r"\bsolution(s)?\b", r"\buse cases?\b",
        r"\bpayments?\b", r"\bdeposits?\b", r"\bverification\b", r"\bpayouts?\b",
        r"\bon-?ramp(s)?\b", r"\boff-?ramp(s)?\b", r"\bstablecoin\b"
    ])

    competition = extract_bullets(md_clean, [
        r"\bcompetitor(s)?\b", r"\bcompetition\b", r"\balternative(s)?\b",
        r"\bvs\.?\b", r"\bcompare\b"
    ])

    deals = extract_bullets(md_clean, [
        r"\bpartner(s|ships)?\b", r"\bcustomer(s)?\b", r"\bintegrat(e|ion)\b",
        r"\bagreement(s)?\b", r"\bcontract(s)?\b", r"\btrusted by\b",
        r"\bfeatured in\b"
    ])

    technologies = extract_bullets(md_clean, [
        r"\bapi(s)?\b", r"\bdeveloper(s)?\b", r"\bintegration\b",
        r"\bstablecoin(s)?\b", r"\bsettlement\b", r"\binfrastructure\b",
        r"\bsecurity\b", r"\bcompliance\b", r"\btoken(s)?\b", r"\bchain(s)?\b"
    ])

    key_people = extract_bullets(md_clean, [
        r"\bfounded by\b", r"\bfounder(s)?\b", r"\bceo\b", r"\bcto\b", r"\bcfo\b",
        r"\bleadership\b", r"\bteam\b", r"\bboard\b"
    ])

    funding = extract_bullets(md_clean, [
        r"\brais(ed|e)\b", r"\bfunding\b", r"\bseed\b", r"\bseries\s+[a-e]\b",
        r"\binvest(or|ors)\b", r"\bvaluation\b", r"\bfinancing\b"
    ])

    report = f"""# Company / Website Intelligence Report

**Source URL:** {url}

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
        raw = raw_md.strip()
        if len(raw) > RAW_MAX_CHARS:
            raw = raw[:RAW_MAX_CHARS] + "\n\n... (truncated) ..."
        report += f"\n---\n\n## Raw extracted Markdown\n{raw}\n"

    return report


async def crawl_one(url: str) -> str:
    async with AsyncWebCrawler() as crawler:
        # Keep it simple/stable. Crawl4AI will use Playwright internally.
        result = await crawler.arun(url)
        return (result.markdown or "").strip()


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

    for i, url in enumerate(urls, start=1):
        if esc_pressed():
            print("\n[INTERRUPT] ESC pressed. Stopping.")
            return

        print(f"[{i}/{len(urls)}] Crawling: {url}")
        try:
            md = await crawl_one(url)

            if esc_pressed():
                print("\n[INTERRUPT] ESC pressed. Stopping.")
                return

            report = build_report(url, md)
            print(report)

        except Exception as e:
            print(f"[ERROR] {url} -> {type(e).__name__}: {e}")
            if esc_pressed():
                print("\n[INTERRUPT] ESC pressed. Stopping.")
                return

    print("\nDone.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INTERRUPT] Ctrl+C pressed. Exiting.")
        sys.exit(0)
