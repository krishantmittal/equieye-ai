# services/llm_client.py
"""
Groq client construction, HTML sanitization for LLM output, and the
direct-call (no-cache) fallback path used when modules/ fails to import.

Extracted from app.py's get_client() / sanitize_llm_html() / the fallback
branch of ask_llm() verbatim. The cached/smart path (ask_llm_smart, via
modules/llm_utils.py) stays a thin branch in app.py's ask_llm() wrapper,
since it already depends on _MODULES_LOADED — app.py's own flag for
whether the whole modules/ package imported cleanly, not just llm_utils.
"""

from __future__ import annotations
import html as _html
import re as _re
from groq import Groq


def get_client(api_key: str) -> Groq:
    return Groq(api_key=api_key)


def ask_llm_fallback(client: Groq, prompt: str, system: str = "", max_tokens: int = 1000,
                      model: str = "openai/gpt-oss-120b") -> str:
    """Direct, uncached Groq call with friendly error messages. Used only
    when modules/llm_utils.py's cached ask_llm_smart() isn't available."""
    try:
        msg = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=0.3,
            messages=[
                {"role": "system", "content": system or "You are EquiEye AI, an expert financial analyst focused on Indian stock markets. Be concise, insightful, and always add a disclaimer that this is not financial advice."},
                {"role": "user", "content": prompt}
            ]
        )
        return msg.choices[0].message.content
    except Exception as e:
        error_text = str(e).lower()
        if "api key" in error_text or "authentication" in error_text or "unauthorized" in error_text:
            friendly = "AI analysis is unavailable right now — there's an issue with the API key configuration. Please check your Groq API key in secrets.toml."
        elif "rate limit" in error_text or "429" in error_text:
            friendly = "AI analysis is temporarily unavailable due to rate limits. Please wait 30 seconds and try again."
        elif "credit" in error_text or "quota" in error_text or "billing" in error_text:
            friendly = "AI analysis is unavailable — the API account has run out of available credits or quota."
        else:
            friendly = "AI analysis couldn't be generated right now. Please try again in a moment."
        return f"⚠ {friendly}"


def sanitize_llm_html(text: str) -> str:
    """
    Escapes HTML special characters in LLM-generated text before it is
    injected into a raw-HTML render block.

    LLM outputs are not user-controlled, but a misbehaving or jailbroken
    model could return <script> tags or other HTML that would execute in
    the browser if passed straight through. This function strips that risk
    while preserving newlines as <br> tags so multi-sentence responses
    still render readably.

    Intentionally does NOT escape apostrophes (') or quotes (") because they
    appear in normal financial prose and escaping them would corrupt text like
    "Tata's revenue" or "D/E of 0.5x (manageable)".

    Also converts the LLM's markdown-style **bold** and *italic* emphasis
    into real <b>/<i> tags — otherwise the literal asterisks leak straight
    into the rendered output since this text is injected as raw HTML, not
    run through a markdown renderer.
    """
    if not text:
        return ""
    escaped = _html.escape(text, quote=False)
    # Markdown bold/italic -> real HTML tags. Bold must run before italic so
    # "**word**" isn't first split into two "*word*" italic matches.
    escaped = _re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)
    escaped = _re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", escaped)
    # Restore newlines as HTML line breaks for readable multi-line output
    escaped = escaped.replace("\n", "<br>")
    return escaped
