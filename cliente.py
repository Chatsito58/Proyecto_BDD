from __future__ import annotations

from conexion.conexion import ConexionBD


def menu_cliente(conexion: ConexionBD, correo: str) -> None:
    """Loop de menú para clientes."""
    while True:
        print("\n--- Menú Cliente ---")
        print("1. Ver vehículos disponibles")
        print("2. Realizar una reserva")
        print("3. Cancelar/modificar reservas")
        print("4. Ver historial de alquileres")
        print("5. Actualizar mis datos")
        print("6. Ver tarifas/promociones")
        print("7. Ver sucursales")
        print("0. Salir")
        opcion = input("Seleccione una opción: ").strip()
        if opcion == "1":
            ver_vehiculos_disponibles(conexion)
        elif opcion == "2":
            realizar_reserva(conexion, correo)
        elif opcion == "3":
            cancelar_reserva(conexion, correo)
        elif opcion == "4":
            ver_historial(conexion, correo)
        elif opcion == "5":
            actualizar_datos(conexion, correo)
        elif opcion == "6":
            ver_tarifas(conexion)
        elif opcion == "7":
            ver_sucursales(conexion)
        elif opcion == "0":
            break
        else:
            print("Opción inválida")


def ver_vehiculos_disponibles(conexion: ConexionBD) -> None:
    try:
        filas = conexion.ejecutar(
            "SELECT placa, modelo FROM Vehiculo LIMIT 10"
        )
        for placa, modelo in filas:
            print(f"Placa: {placa} - Modelo: {modelo}")
    except Exception as exc:  # pragma: no cover - depende de la BD
        print("Error obteniendo vehículos:", exc)


def realizar_reserva(conexion: ConexionBD, correo: str) -> None:
    print("Función de reserva no implementada")


def cancelar_reserva(conexion: ConexionBD, correo: str) -> None:
    print("Función de cancelación/modificación no implementada")


def ver_historial(conexion: ConexionBD, correo: str) -> None:
    print("Función de historial no implementada")


def actualizar_datos(conexion: ConexionBD, correo: str) -> None:
    print("Función de actualización de datos no implementada")


def ver_tarifas(conexion: ConexionBD) -> None:
    try:
        filas = conexion.ejecutar("SELECT descripcion, valor FROM Descuento_alquiler")
        if not filas:
            print("No hay tarifas o promociones registradas")
        for desc, valor in filas:
            print(f"{desc}: {valor}")
    except Exception as exc:  # pragma: no cover - depende de la BD
        print("Error consultando tarifas:", exc)


def ver_sucursales(conexion: ConexionBD) -> None:
    print("Función de consulta de sucursales no implementada")
