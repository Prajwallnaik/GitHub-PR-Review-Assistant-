"""Formatting helpers for display elements."""


def format_severity_badge(severity: str) -> str:
    """Format severity as a colored badge string."""
    colors = {
        "low": "#2ECC71",
        "medium": "#F39C12",
        "high": "#E74C3C",
    }
    color = colors.get(severity.lower(), "#95A5A6")
    return (
        f'<span style="background-color:{color};color:white;padding:3px 10px;'
        f'border-radius:12px;font-size:0.85em;font-weight:600;">'
        f'{severity.upper()}</span>'
    )


def format_impact_badge(impact: str) -> str:
    """Format impact level with a colored dot."""
    colors = {
        "low": "#2ECC71",
        "medium": "#F39C12",
        "high": "#E74C3C",
    }
    color = colors.get(impact.lower(), "#95A5A6")
    return (
        f'<span style="display:inline-block;width:10px;height:10px;'
        f'background-color:{color};border-radius:50%;margin-right:6px;vertical-align:middle;"></span>'
        f'**{impact.capitalize()}** impact'
    )



def truncate_string(text: str, max_length: int = 200) -> str:
    """Truncate a string with an ellipsis if it exceeds max_length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
