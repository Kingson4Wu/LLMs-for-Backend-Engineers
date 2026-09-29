"""Shared, non-DRM attribution for publication formats with stable geometry."""
from __future__ import annotations

WATERMARK_ANGLE = -30
# Four-percent black survives in the PDF content stream but is effectively
# invisible in common readers. Eight percent remains quiet behind body copy
# while giving the diagonal attribution a reliably perceptible contrast.
WATERMARK_TINT = "black!8"
WATERMARK_INTERVAL = 3
WATERMARK_TEXT = "Kingson Wu"


def display_text(locale: str) -> str:
    return WATERMARK_TEXT


def provenance_line(locale: str) -> str:
    if locale.startswith("zh"):
        return "版权所有 © Kingson Wu · 正式版本与来源：github.com/Kingson4Wu/Understanding-LLMs"
    return "Copyright © Kingson Wu · Canonical edition: github.com/Kingson4Wu/Understanding-LLMs"


def pdf_subject(locale: str) -> str:
    """Keep machine-readable provenance alongside the visual PDF watermark."""
    return f"Publication watermark · {display_text(locale)}"


def append_provenance(document: dict, locale: str) -> None:
    """Keep one visible ownership line in reflowable EPUB without page overlays."""
    document["blocks"].extend(
        [
            {"t": "HorizontalRule"},
            {"t": "Para", "c": [{"t": "Str", "c": provenance_line(locale)}]},
        ]
    )


def watermark_html(locale: str) -> str:
    return f'<div class="publication-watermark" aria-hidden="true">{display_text(locale)}</div>'


def watermark_tex(locale: str) -> str:
    text = display_text(locale).replace("&", r"\&")
    return "\n".join(
        [
            r"\usepackage{tikz}",
            r"\newif\ifbodywatermark",
            r"\bodywatermarkfalse",
            r"\newcounter{watermarkpage}",
            r"\AddToHook{shipout/background}{%",
            r"  \ifbodywatermark",
            r"    \stepcounter{watermarkpage}",
            rf"    \ifnum\value{{watermarkpage}}={WATERMARK_INTERVAL}",
            r"    \begin{tikzpicture}[remember picture,overlay]",
            rf"      \node[rotate={WATERMARK_ANGLE},text={WATERMARK_TINT},font=\sffamily\bfseries\fontsize{{34pt}}{{34pt}}\selectfont] at (current page.center) {{{text}}};",
            r"    \end{tikzpicture}%",
            r"    \setcounter{watermarkpage}{0}",
            r"    \fi",
            r"  \fi",
            r"}",
        ]
    )
