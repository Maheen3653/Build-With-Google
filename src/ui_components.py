
from pathlib import Path
from html import escape

import streamlit as st


def load_css() -> str:
    """Read the project's CSS file and return its contents."""
    css_path = Path(__file__).resolve().parent.parent / "assets" / "styles.css"
    return css_path.read_text(encoding="utf-8")


def metric_card(label: str, value: str, helper: str) -> None:
    """Display a reusable metric card with a label, value and helper."""
    st.markdown(
        f"""
        <div class="ds-metric">
            <div class="ds-metric-label">{escape(str(label))}</div>
            <div class="ds-metric-value">{escape(str(value))}</div>
            <div class="ds-metric-helper">{escape(str(helper))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def badge(status: str) -> None:
    """Display a Matched, Partial or Missing status badge."""
    styles = {
        "matched": ("Matched", "ds-badge-matched"),
        "partial": ("Partial", "ds-badge-partial"),
        "missing": ("Missing", "ds-badge-missing"),
    }
    label, css_class = styles.get(
        status.lower(),
        (status.title(), "ds-badge-missing")
    )
    st.markdown(
        f'<span class="ds-badge {css_class}">{escape(label)}</span>',
        unsafe_allow_html=True
    )


def empty_state(
    title: str,
    message: str,
    button_label: str,
    target_page: str
) -> None:
    """Show a friendly empty state with a button to another page."""
    st.markdown(
        f"""
        <div class="ds-card">
            <h3>{escape(title)}</h3>
            <p>{escape(message)}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(button_label, key=f"empty_{target_page}"):
        st.session_state["page"] = target_page
        st.rerun()


def illustrative_banner() -> None:
    """Display a notice explaining that role data is illustrative."""
    st.markdown(
        """
        <div class="ds-banner">
            <strong>Illustrative data:</strong>
            Role profiles are provided for demonstration.
            They are not verified market data or live job requirements.
        </div>
        """,
        unsafe_allow_html=True
    )


def ai_block(text: str) -> None:
    """Display AI-generated content with a responsible-use label."""
    st.markdown(
        f"""
        <div class="ds-card">
            <div class="ds-ai-label">
                AI-generated · verify before relying on it
            </div>
            <div>{escape(str(text)).replace(chr(10), '<br>')}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def page_header(title: str, subtitle: str) -> None:
    """Display a consistent page title and subtitle."""
    st.markdown(
        f"""
        <h1>{escape(title)}</h1>
        <p class="ds-page-subtitle">{escape(subtitle)}</p>
        """,
        unsafe_allow_html=True
    )
