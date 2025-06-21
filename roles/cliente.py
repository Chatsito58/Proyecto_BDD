"""Funciones para el rol de cliente."""


def reservar():
    """Registrar una nueva reserva (pendiente de implementación)."""
    print("Función de reserva aún no implementada")


def ver_reservas():
    """Mostrar las reservas del cliente (pendiente de implementación)."""
    print("Función para ver reservas aún no implementada")


def mostrar_menu() -> None:
    """Mostrar menú para clientes."""
    while True:
        print("\n--- Menú Cliente ---")
        print("1. Reservar")
        print("2. Ver mis reservas")
        print("0. Salir")
        opcion = input("Seleccione una opción: ").strip()
        if opcion == "1":
            reservar()
        elif opcion == "2":
            ver_reservas()
        elif opcion == "0":
            break
        else:
            print("Opción inválida")
