"""Summarize article abstracts using the Anthropic API."""
import os

_SYSTEM_PROMPT = (
    "You summarize infectious disease research abstracts for a busy clinician. "
    "Given a paper's title and abstract, write a 2-3 sentence plain-language summary "
    "covering: what was studied, the key finding, and why it matters clinically. "
    "No preamble, no markdown headers."
)


def summarize_article(article, model):
    """Return a short summary string for one article dict, or the raw abstract if no API key is set."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return article["abstract"]

    from anthropic import Anthropic

    client = Anthropic(api_key=api_key)
    user_content = f"Title: {article['title']}\n\nAbstract:\n{article['abstract']}"

    try:
        response = client.messages.create(
            model=model,
            max_tokens=300,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )
        return response.content[0].text.strip()
    except Exception as exc:  # noqa: BLE001 - fall back rather than fail the whole digest
        return f"(summary unavailable: {exc})\n\n{article['abstract']}"


def summarize_articles(articles, model):
    for article in articles:
        article["summary"] = summarize_article(article, model)
    return articles
