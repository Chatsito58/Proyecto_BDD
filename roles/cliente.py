from __future__ import annotations

from conexion.conexion import ConexionBD


def realizar_abono(id_cliente: int) -> None:
    """Permitir al cliente registrar un abono para una de sus reservas pendientes."""
    conexion = ConexionBD()

    # Obtener identificador de estado "pendiente" (o "reservado" como respaldo)
    id_estado = None
    try:
        res = conexion.ejecutar(
            "SELECT id_estado FROM Estado_reserva WHERE LOWER(descripcion)='pendiente'"
        )
        if res:
            id_estado = int(res[0][0])
        else:
            res = conexion.ejecutar(
                "SELECT id_estado FROM Estado_reserva WHERE LOWER(descripcion)='reservado'"
            )
            id_estado = int(res[0][0]) if res else None
    except Exception as exc:
        print("Error obteniendo estados:", exc)
        return

    # Buscar reservas pendientes del cliente
    query = (
        "SELECT r.id_reserva, (r.abono + r.saldo_pendiente) AS total, "
        "COALESCE(SUM(a.valor),0) AS abonado "
        "FROM Reserva_alquiler r "
        "LEFT JOIN Abono_reserva a ON r.id_reserva=a.id_reserva "
        "WHERE r.id_cliente=%s "
    )
    params = [id_cliente]
    if id_estado is not None:
        query += "AND r.id_estado_reserva=%s "
        params.append(id_estado)
    query += "GROUP BY r.id_reserva, r.abono, r.saldo_pendiente"

    try:
        filas = conexion.ejecutar(query, tuple(params))
    except Exception as exc:
        print("Error consultando reservas:", exc)
        return

    if not filas:
        print("No tiene reservas pendientes.")
        return

    print("Reservas pendientes:")
    for idx, (id_reserva, total, abonado) in enumerate(filas, start=1):
        restante = float(total) - float(abonado)
        print(f"{idx}. Reserva #{id_reserva} - Saldo restante: ${restante:.2f}")

    # Selección
    seleccion = None
    while seleccion is None:
        opcion = input("Seleccione una reserva: ").strip()
        if opcion.isdigit() and 1 <= int(opcion) <= len(filas):
            seleccion = int(opcion) - 1
        else:
            print("Opción inválida")

    id_reserva, total, abonado = filas[seleccion]
    restante = float(total) - float(abonado)
    print(f"Total: ${float(total):.2f}")
    print(f"Abonado: ${float(abonado):.2f}")
    print(f"Saldo restante: ${restante:.2f}")

    monto = None
    while monto is None:
        monto_str = input("Monto a abonar: ").strip()
        try:
            monto_val = float(monto_str)
        except ValueError:
            print("Monto inválido")
            continue
        if monto_val > restante:
            print("El monto no puede superar el saldo restante")
            continue
        if monto_val <= 0:
            print("El monto debe ser positivo")
            continue
        monto = monto_val

    # Registrar abono
    try:
        conexion.ejecutar(
            "INSERT INTO Abono_reserva (valor, fecha_hora, id_reserva) VALUES (%s, NOW(), %s)",
            (monto, id_reserva),
        )
        print("Abono registrado correctamente.")
    except Exception as exc:
        print("Error registrando abono:", exc)
=======
def _print_table(headers: list[str], rows: list[tuple]) -> None:
    """Print rows as a simple table."""
    if not rows:
        return
    col_widths = []
    for i, head in enumerate(headers):
        max_len = len(str(head))
        for row in rows:
            val = str(row[i])
            if len(val) > max_len:
                max_len = len(val)
        col_widths.append(max_len)
    header_line = " | ".join(str(h).ljust(col_widths[i]) for i, h in enumerate(headers))
    separator = "-+-".join("-" * w for w in col_widths)
    print(header_line)
    print(separator)
    for row in rows:
        line = " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(headers)))
        print(line)


def ver_reservas(id_cliente: int) -> None:
    """Consultar e imprimir las reservas de un cliente."""
    conn = ConexionBD()
    query = (
        "SELECT r.id_reserva, COALESCE(tv.descripcion, 'N/A') AS tipo, "
        "r.fecha_hora_salida, r.fecha_hora_entrada, er.descripcion "
        "FROM Reserva_alquiler r "
        "JOIN Estado_reserva er ON r.id_estado_reserva=er.id_estado "
        "LEFT JOIN Alquiler a ON r.id_alquiler=a.id_alquiler "
        "LEFT JOIN Vehiculo v ON a.id_vehiculo=v.placa "
        "LEFT JOIN Tipo_vehiculo tv ON v.id_tipo_vehiculo=tv.id_tipo "
        "WHERE r.id_cliente=%s "
        "ORDER BY r.fecha_hora_salida"
    )
    try:
        filas = conn.ejecutar(query, (id_cliente,))
    except Exception as exc:  # pragma: no cover - depende de la BD
        print("Error consultando reservas:", exc)
        return
    if not filas:
        print("No hay reservas registradas para este cliente.")
        return
    headers = ["ID", "Tipo", "Inicio", "Fin", "Estado"]
    _print_table(headers, filas)
=======
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
