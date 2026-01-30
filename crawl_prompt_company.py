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
        # ESC is 27 (b'\x1b')
        return ch == b"\x1b"
    return False


def find_first_h1(markdown: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def strip_md(md: str) -> str:
    """Lightweight cleanup: remove excessive whitespace."""
    md = md.replace("\r\n", "\n")
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return md


def extract_snippets(md: str, patterns: list[str], max_snippets: int = 6) -> list[str]:
    """
    Extract short text snippets around keywords/patterns from markdown.
    This is heuristic: good enough for quick analyst-style summaries.
    """
    text = re.sub(r"\s+", " ", md)
    snippets = []

    for pat in patterns:
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            start = max(0, m.start() - 180)
            end = min(len(text), m.end() + 220)
            snippet = text[start:end].strip()
            # De-duplicate
            if snippet and snippet not in snippets:
                snippets.append(snippet)
            if len(snippets) >= max_snippets:
                return snippets

    return snippets


def md_bullets(items: list[str]) -> str:
    if not items:
        return "- *(not found on page)*"
    # trim overly long lines
    cleaned = []
    for s in items:
        s = s.strip()
        if len(s) > 300:
            s = s[:300].rstrip() + "…"
        cleaned.append(s)
    return "\n".join(f"- {s}" for s in cleaned)


def build_structured_markdown(url: str, raw_md: str) -> str:
    md = strip_md(raw_md)
    title = find_first_h1(md) or urlparse(url).netloc

    # Heuristic patterns (you can tune these later per your sources)
    sector = extract_snippets(md, [
        r"\bindustr(y|ies)\b", r"\bsector\b", r"\bmarket\b", r"\bvertical\b",
        r"\bfintech\b|\bsaas\b|\bsecurity\b|\bdefen[cs]e\b|\bhealt?h\b|\bai\b"
    ])

    products = extract_snippets(md, [
        r"\bproduct(s)?\b", r"\bplatform\b", r"\bsolution(s)?\b",
        r"\bservice(s)?\b", r"\boffer(s|ing)?\b", r"\bfeatures?\b"
    ])

    competition = extract_snippets(md, [
        r"\bcompetitor(s)?\b", r"\bcompetition\b", r"\balternative(s)?\b",
        r"\bversus\b", r"\bcompare\b"
    ])

    deals = extract_snippets(md, [
        r"\bdeal(s)?\b", r"\bpartnership(s)?\b", r"\bcustomer(s)?\b",
        r"\bcontract(s)?\b", r"\bagreement(s)?\b"
    ])

    technologies = extract_snippets(md, [
        r"\btechnolog(y|ies)\b", r"\bstack\b", r"\binfrastructure\b",
        r"\bapi(s)?\b", r"\bmodel(s)?\b", r"\bllm\b", r"\bmachine learning\b",
        r"\bcomputer vision\b", r"\bplaywright\b", r"\bkubernetes\b"
    ])

    key_people = extract_snippets(md, [
        r"\bteam\b", r"\bfounded by\b", r"\bfounder(s)?\b",
        r"\bceo\b|\bcto\b|\bcfo\b|\bcoo\b", r"\bleadership\b", r"\bboard\b"
    ])

    funding_rounds = extract_snippets(md, [
        r"\brais(ed|e)\b", r"\bfunding\b", r"\bseed\b", r"\bseries\s+[a-e]\b",
        r"\binvest(or|ors)\b", r"\bvaluation\b"
    ])

    # Output: structured markdown report + original extracted markdown below
    report = f"""# Company / Website Intelligence Report

**Source URL:** {url}

## Company name
- **{title}**

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
{md_bullets(funding_rounds)}

---

## Raw extracted Markdown
{md}
"""
    return report


async def crawl_one(url: str) -> str:
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url)
        return (result.markdown or "").strip()


async def main():
    print('Enter website URL(s) to crawl (comma-separated).')
    print('Tip: press ESC anytime to stop.\n')

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
        # ESC interrupt check before each URL
        if esc_pressed():
            print("\n[INTERRUPT] ESC pressed. Stopping.")
            return

        print(f"[{i}/{len(urls)}] Crawling: {url}")
        try:
            md = await crawl_one(url)

            # ESC interrupt check after crawling
            if esc_pressed():
                print("\n[INTERRUPT] ESC pressed. Stopping.")
                return

            report = build_structured_markdown(url, md)
            print(report)

        except Exception as e:
            print(f"[ERROR] {url} -> {type(e).__name__}: {e}")
            # ESC interrupt check even on errors
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
