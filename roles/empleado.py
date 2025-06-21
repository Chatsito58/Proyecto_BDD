"""Funciones para el rol de empleado."""


def registrar_pago():
    """Registrar un pago de un cliente (pendiente de implementación)."""
    print("Función de registrar pago aún no implementada")


def ver_abonos():
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
