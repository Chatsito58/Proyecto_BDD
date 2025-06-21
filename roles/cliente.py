from __future__ import annotations

from datetime import datetime

from conexion.conexion import ConexionBD


def realizar_reserva(id_cliente: int) -> None:
    """Registrar una nueva reserva para el cliente indicado."""
    conexion = ConexionBD()
    tipo = input("Tipo de vehículo: ").strip()
    fecha_ini_str = input("Fecha inicio (YYYY-MM-DD): ").strip()
    fecha_fin_str = input("Fecha fin (YYYY-MM-DD): ").strip()

    try:
        fecha_ini = datetime.strptime(fecha_ini_str, "%Y-%m-%d").date()
        fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
    except ValueError:
        print("Formato de fecha inválido. Use YYYY-MM-DD")
        return

    if fecha_fin <= fecha_ini:
        print("La fecha de fin debe ser posterior a la de inicio")
        return

    dias = (fecha_fin - fecha_ini).days + 1
    total = dias * 100000
    abono_minimo = total * 0.3
    print(f"Total a pagar: ${total:,.0f}")
    print(f"Abono mínimo: ${abono_minimo:,.0f}")

    monto_str = input("Valor a abonar: ").strip()
    try:
        monto = float(monto_str)
    except ValueError:
        print("El abono debe ser numérico")
        return
    if monto < abono_minimo:
        print("El valor abonado es inferior al mínimo requerido")
        return

    try:
        conexion.ejecutar(
            "INSERT INTO reserva (id_cliente, tipo_vehiculo, fecha_inicio, fecha_fin, estado) "
            "VALUES (%s, %s, %s, %s, %s)",
            (
                id_cliente,
                tipo,
                fecha_ini.strftime("%Y-%m-%d"),
                fecha_fin.strftime("%Y-%m-%d"),
                "pendiente",
            ),
        )
        id_reserva = conexion.ejecutar("SELECT LAST_INSERT_ID()")[0][0]
        conexion.ejecutar(
            "INSERT INTO abono_reserva (id_reserva, monto_abonado, fecha_abono) "
            "VALUES (%s, %s, NOW())",
            (id_reserva, monto),
        )
        print("Reserva registrada correctamente")
    except Exception as exc:  # pragma: no cover - depende de la BD
        print("Error registrando la reserva:", exc)
