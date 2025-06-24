"""Funciones para el rol de empleado."""

from __future__ import annotations

from conexion.conexion import ConexionBD


def registrar_pago() -> None:
    """Registrar un pago de un cliente (pendiente de implementación)."""
    print("Función de registrar pago aún no implementada")


def ver_abonos() -> None:
    """Mostrar abonos registrados (pendiente de implementación)."""
    print("Función para ver abonos aún no implementada")

def registrar_reserva(conexion: ConexionBD) -> None:
    print("Función de registrar reserva no implementada")


def confirmar_entrega(conexion: ConexionBD) -> None:
    print("Función de confirmación de entrega/devolución no implementada")


def ver_flota(conexion: ConexionBD) -> None:
    print("Función de consulta de flota no implementada")


def registrar_danio(conexion: ConexionBD) -> None:
    print("Función de registro de daños no implementada")


def historial_cliente(conexion: ConexionBD) -> None:
    print("Función de historial por cliente no implementada")


def notificar_clientes(conexion: ConexionBD) -> None:
    print("Función de notificación via Twilio no implementada")


def disponibilidad_sede(conexion: ConexionBD) -> None:
    print("Función de disponibilidad por sede no implementada")
