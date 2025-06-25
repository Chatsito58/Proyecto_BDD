import logging

# Logger to be imported across the project
logger = logging.getLogger(__name__)


def configurar_logging() -> None:
    """Configure root logging with INFO level and standard format."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
