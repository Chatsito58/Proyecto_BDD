"""Funciones para el rol de administrador."""


def alta_usuario():
    """Dar de alta un nuevo usuario (pendiente de implementación)."""
    print("Función para dar de alta usuarios aún no implementada")


def mostrar_menu() -> None:
    """Mostrar menú para administradores."""
    while True:
        print("\n--- Menú Administrador ---")
        print("1. Dar de alta usuario")
        print("0. Salir")
        opcion = input("Seleccione una opción: ").strip()
        if opcion == "1":
            alta_usuario()
        elif opcion == "0":
            break
        else:
            print("Opción inválida")
