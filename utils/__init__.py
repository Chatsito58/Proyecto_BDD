def safe_bg_error_handler(*_args) -> None:
    """Global handler for exceptions raised in Tk callbacks."""
    import traceback

    print("Error capturado en bgerror:")
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

