"""Plantilla para integrar Twilio API."""

from typing import Any


class TwilioAPI:
    def enviar_mensaje(self, numero: str, mensaje: str) -> Any:
        raise NotImplementedError
