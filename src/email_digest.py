"""Build and send the HTML digest email via Gmail SMTP."""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

_SECTION_LABELS = (
    ("introduction", "Introduction"),
    ("methods", "Methods"),
    ("results", "Results"),
    ("discussion", "Discussion"),
    ("conclusion", "Conclusion"),
)


def _build_sections_html(article_sections):
    parts = []
    for key, label in _SECTION_LABELS:
        text = article_sections.get(key)
        if not text:
            continue
        parts.append(f'<p style="margin:0 0 4px;"><strong>{label}:</strong> {text}</p>')
    return "".join(parts)


def build_html(articles):
    if not articles:
        return "<p>No new infectious disease articles today.</p>"

    sections = []
    for article in articles:
        authors = ", ".join(article["authors"][:5])
        if len(article["authors"]) > 5:
            authors += ", et al."
        sections.append(
            f"""
            <div style="margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid #ddd;">
                <h3 style="margin:0 0 4px;"><a href="{article['link']}">{article['title']}</a></h3>
                <p style="margin:0 0 4px;color:#555;font-size:13px;">{article['journal']} &mdash; {authors}</p>
                {_build_sections_html(article["sections"])}
            </div>
            """
        )
    return f"<div>{''.join(sections)}</div>"


def send_digest(recipient, sender, app_password, articles):
    html = build_html(articles)
    subject = f"Infectious Disease Digest — {len(articles)} new article(s)"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, app_password)
        server.sendmail(sender, [recipient], msg.as_string())
