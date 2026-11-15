"""
Plot export utilities for PNG and vector PDF figures.
"""

from matplotlib.figure import Figure


def save_figure(fig: Figure, filepath: str, dpi: int = 300) -> None:
    """
    Saves a Matplotlib Figure to disk with tight layout and high resolution.
    Supports .png, .pdf, .svg, and .jpg extensions.
    """
    fig.savefig(filepath, dpi=dpi, bbox_inches="tight")
