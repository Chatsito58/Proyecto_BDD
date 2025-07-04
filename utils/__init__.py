from utils.logger import logger


def safe_bg_error_handler(*_args) -> None:
    """Global handler for exceptions raised in Tk callbacks."""
    import traceback

    logger.error("Error capturado en bgerror:")
    traceback.print_exc()


def cancel_pending_after(widget) -> None:
    """Cancel any scheduled callbacks stored in ``widget._after_ids``."""
    for after_id in getattr(widget, "_after_ids", []):
        try:
            widget.after_cancel(after_id)
        except Exception:
            pass
    if hasattr(widget, "_after_ids"):
        widget._after_ids.clear()

from .errores import mostrar_error, mostrar_notificacion

__all__ = [
    "safe_bg_error_handler",
    "cancel_pending_after",
    "mostrar_error",
    "mostrar_notificacion",
]

