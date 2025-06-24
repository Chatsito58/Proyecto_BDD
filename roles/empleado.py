"""Funciones para el rol de empleado."""

from __future__ import annotations

from conexion.conexion import ConexionBD


def registrar_pago() -> None:
    """Registrar un pago de un cliente (pendiente de implementación)."""
    print("Función de registrar pago aún no implementada")


def ver_abonos() -> None:
    """Mostrar abonos registrados (pendiente de implementación)."""
    print("Función para ver abonos aún no implementada")


def mostrar_menu() -> None:
    """Mostrar menú para empleados."""
    while True:
        print("\n--- Menú Empleado ---")
        print("1. Registrar pago")
        print("2. Ver abonos")
        print("0. Salir")
        opcion = input("Seleccione una opción: ").strip()
        if opcion == "1":
            registrar_pago()
        elif opcion == "2":
            ver_abonos()
        elif opcion == "0":
            break
        else:
            print("Opción inválida")


def menu_empleado(conexion: ConexionBD, correo: str) -> None:
    """Menú completo de opciones para empleados del sistema."""
    while True:
        print("\n--- Menú Empleado ---")
        print("1. Registrar reserva para cliente")
        print("2. Confirmar entrega/devolución")
        print("3. Ver estado de la flota")
        print("4. Registrar daños/incidentes")
        print("5. Consultar historial por cliente")
        print("6. Notificar a clientes")
        print("7. Ver disponibilidad por sede")
        print("0. Salir")
        op = input("Seleccione una opción: ").strip()
        if op == "1":
            registrar_reserva(conexion)
        elif op == "2":
            confirmar_entrega(conexion)
        elif op == "3":
            ver_flota(conexion)
        elif op == "4":
            registrar_danio(conexion)
        elif op == "5":
            historial_cliente(conexion)
        elif op == "6":
            notificar_clientes(conexion)
        elif op == "7":
            disponibilidad_sede(conexion)
        elif op == "0":
            break
        else:
            print("Opción inválida")


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
