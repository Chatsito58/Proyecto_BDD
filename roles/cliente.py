from __future__ import annotations

from datetime import datetime

from conexion.conexion import ConexionBD


# ------------------------------

def mostrar_menu_cliente(id_cliente: int) -> None:
    """Menú de acciones disponibles para el cliente."""
    while True:
        print("\n--- Menú Cliente ---")
        print("1. Realizar nueva reserva")
        print("2. Ver reservas activas")
        print("3. Realizar abono")
        print("4. Ver estado de pago")
        print("0. Salir")
        opcion = input("Seleccione una opción: ").strip()
        if opcion == "1":
            realizar_reserva(id_cliente)
        elif opcion == "2":
            ver_reservas(id_cliente)
        elif opcion == "3":
            realizar_abono(id_cliente)
        elif opcion == "4":
            estado_pago(id_cliente)
        elif opcion == "0":
            break
        else:
            print("Opción inválida")


# ------------------------------

def _input_fechas() -> tuple[str, str] | None:
    """Solicitar fechas y retornarlas en formato adecuado."""
    ini = input("Fecha inicio (YYYY-MM-DD): ").strip()
    fin = input("Fecha fin (YYYY-MM-DD): ").strip()
    try:
        d_ini = datetime.strptime(ini, "%Y-%m-%d")
        d_fin = datetime.strptime(fin, "%Y-%m-%d")
    except ValueError:
        print("Formato de fecha inválido")
        return None
    if d_fin < d_ini:
        print("La fecha final debe ser posterior a la inicial")
        return None
    return d_ini.strftime("%Y-%m-%d %H:%M:%S"), d_fin.strftime("%Y-%m-%d %H:%M:%S")


# ------------------------------

def realizar_reserva(id_cliente: int) -> None:
    """Crear una reserva mínima con abono inicial del 30%."""
    fechas = _input_fechas()
    if fechas is None:
        return
    fecha_ini, fecha_fin = fechas
    tipo = input("Tipo de vehículo: ").strip()
    if not tipo:
        print("Debe indicar el tipo de vehículo")
        return
    # Monto base fijo por día (ejemplo)
    tarifa_dia = 100.0
    dias = (datetime.strptime(fecha_fin, "%Y-%m-%d %H:%M:%S") - datetime.strptime(fecha_ini, "%Y-%m-%d %H:%M:%S")).days + 1
    total = dias * tarifa_dia
    abono = total * 0.3
    restante = total - abono

    query_reserva = (
        "INSERT INTO Reserva_alquiler (fecha_hora, fecha_hora_entrada, fecha_hora_salida, "
        "abono, saldo_pendiente, id_cliente, id_estado_reserva) "
        "VALUES (NOW(), %s, %s, %s, %s, %s, 1)"
    )
    query_abono = (
        "INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva, id_medio_pago) "
        "VALUES (%s, NOW(), %s, 1)"
    )
    conn = ConexionBD()
    try:
        conn.ejecutar(query_reserva, (fecha_fin, fecha_ini, abono, restante, id_cliente))
        res = conn.ejecutar("SELECT LAST_INSERT_ID()")
        id_reserva = int(res[0][0]) if res else None
        if id_reserva:
            conn.ejecutar(query_abono, (abono, id_reserva))
        print(f"Reserva creada con ID {id_reserva} y abono de {abono:.2f}")
    except Exception as exc:  # pragma: no cover - depende de la BD
        print("Error al crear la reserva:", exc)


# ------------------------------

def ver_reservas(id_cliente: int) -> None:
    """Mostrar reservas activas del cliente."""
    query = (
        "SELECT r.id_reserva, r.fecha_hora_salida, r.fecha_hora_entrada, er.descripcion "
        "FROM Reserva_alquiler r JOIN Estado_reserva er ON r.id_estado_reserva=er.id_estado "
        "WHERE r.id_cliente=%s"
    )
    conn = ConexionBD()
    try:
        filas = conn.ejecutar(query, (id_cliente,))
        if not filas:
            print("No tiene reservas registradas")
            return
        for rid, salida, entrada, estado in filas:
            print(f"Reserva {rid} | {salida} -> {entrada} | Estado: {estado}")
    except Exception as exc:  # pragma: no cover - depende de la BD
        print("Error consultando reservas:", exc)


# ------------------------------

def realizar_abono(id_cliente: int) -> None:
    """Permitir registrar un abono adicional."""
    query = (
        "SELECT r.id_reserva, r.abono + r.saldo_pendiente AS total, "
        "COALESCE(SUM(a.valor),0) AS pagado "
        "FROM Reserva_alquiler r "
        "LEFT JOIN Abono_reserva a ON r.id_reserva=a.id_reserva "
        "WHERE r.id_cliente=%s "
        "GROUP BY r.id_reserva, r.abono, r.saldo_pendiente "
        "HAVING pagado < total"
    )
    conn = ConexionBD()
    try:
        filas = conn.ejecutar(query, (id_cliente,))
    except Exception as exc:  # pragma: no cover - depende de la BD
        print("Error obteniendo reservas:", exc)
        return
    if not filas:
        print("No hay reservas pendientes de pago")
        return
    pendientes: dict[int, float] = {}
    for rid, total, pagado in filas:
        restante = float(total) - float(pagado)
        pendientes[int(rid)] = restante
        print(f"Reserva {rid} - Saldo restante: {restante:.2f}")
    try:
        sel = int(input("ID de reserva a abonar: ").strip())
    except ValueError:
        print("ID inválido")
        return
    if sel not in pendientes:
        print("Reserva no válida")
        return
    restante = pendientes[sel]
    monto_str = input("Monto a abonar: ").strip()
    try:
        monto = float(monto_str)
    except ValueError:
        print("Monto inválido")
        return
    if monto < restante * 0.3:
        print("Debe abonar al menos el 30% del saldo restante")
        return
    query_ins = (
        "INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva, id_medio_pago) "
        "VALUES (%s, NOW(), %s, 1)"
    )
    try:
        conn.ejecutar(query_ins, (monto, sel))
        print("Abono registrado")
    except Exception as exc:  # pragma: no cover - depende de la BD
        print("Error registrando abono:", exc)


# ------------------------------

def estado_pago(id_cliente: int) -> None:
    """Mostrar total reservado y lo abonado por cada reserva."""
    query = (
        "SELECT r.id_reserva, r.abono + r.saldo_pendiente AS total, "
        "COALESCE(SUM(a.valor),0) AS pagado "
        "FROM Reserva_alquiler r "
        "LEFT JOIN Abono_reserva a ON r.id_reserva=a.id_reserva "
        "WHERE r.id_cliente=%s "
        "GROUP BY r.id_reserva, r.abono, r.saldo_pendiente"
    )
    conn = ConexionBD()
    try:
        filas = conn.ejecutar(query, (id_cliente,))
    except Exception as exc:  # pragma: no cover - depende de la BD
        print("Error consultando estado de pagos:", exc)
        return
    if not filas:
        print("No tiene reservas registradas")
        return
    for rid, total, pagado in filas:
        restante = float(total) - float(pagado)
        estado = "COMPLETO" if restante <= 0 else f"Falta {restante:.2f}"
        print(f"Reserva {rid} - Total {total:.2f} - Pagado {pagado:.2f} -> {estado}")
