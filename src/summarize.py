"""Summarize article abstracts, broken into sections, using the OpenAI API."""
import json
import os

_SYSTEM_PROMPT = (
    "You summarize infectious disease research abstracts for a busy clinician. "
    "Given a paper's title and abstract, write a plain-language summary broken into "
    "five sections: introduction, methods, results, discussion, conclusion. "
    "Each section should be 1-2 sentences, no preamble, no markdown headers. "
    'Respond with a JSON object with exactly these keys: "introduction", "methods", '
    '"results", "discussion", "conclusion".'
)

_SECTION_KEYS = ("introduction", "methods", "results", "discussion", "conclusion")

_EMPTY_SECTIONS = {key: "" for key in _SECTION_KEYS}


def _raw_abstract_sections(article):
    return {**_EMPTY_SECTIONS, "introduction": article["abstract"]}


def summarize_article(article, model):
    """Return a dict of the five section summaries for one article, or the raw
    abstract under "introduction" (other sections blank) if no API key is set
    or the API call fails."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return _raw_abstract_sections(article)

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    user_content = f"Title: {article['title']}\n\nAbstract:\n{article['abstract']}"

    try:
        response = client.chat.completions.create(
            model=model,
            max_tokens=500,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )
        parsed = json.loads(response.choices[0].message.content)
        return {key: str(parsed.get(key, "")).strip() for key in _SECTION_KEYS}
    except Exception as exc:  # noqa: BLE001 - fall back rather than fail the whole digest
        print(f"Warning: summary unavailable for PMID {article.get('pmid')}: {exc}")
        return _raw_abstract_sections(article)


def summarize_articles(articles, model):
    for article in articles:
        article["sections"] = summarize_article(article, model)
    return articles
