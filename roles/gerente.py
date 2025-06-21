"""Funciones para el rol de gerente."""


def generar_reporte():
    """Generar reportes de gestión (pendiente de implementación)."""
    print("Función de generación de reportes aún no implementada")


def mostrar_menu() -> None:
    """Mostrar menú para gerentes."""
    while True:
        print("\n--- Menú Gerente ---")
        print("1. Generar reportes")
        print("0. Salir")
        opcion = input("Seleccione una opción: ").strip()
        if opcion == "1":
            generar_reporte()
        elif opcion == "0":
            break
        else:
            print("Opción inválida")
