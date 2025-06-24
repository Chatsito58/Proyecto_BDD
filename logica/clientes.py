from __future__ import annotations

from conexion.conexion import ConexionBD
from utils.hash_utils import sha256_hash
from utils.validations import validar_correo


class DatosClienteInvalidos(ValueError):
    """Excepción para datos inválidos del cliente."""


def crear_cliente(
    documento: str,
    nombre: str,
    telefono: str,
    direccion: str,
    correo: str,
    contrasena: str,
    id_licencia: str,
    id_tipo_documento: str,
    id_tipo_cliente: str,
    id_codigo_postal: str,
) -> None:
    """Crear un nuevo cliente en la base de datos."""

    campos = [
        documento,
        nombre,
        telefono,
        direccion,
        correo,
        contrasena,
        id_licencia,
        id_tipo_documento,
        id_tipo_cliente,
        id_codigo_postal,
    ]
    if not all(campos):
        raise DatosClienteInvalidos("Todos los campos son obligatorios")
    if not validar_correo(correo):
        raise DatosClienteInvalidos("Correo no válido")

    hashed = sha256_hash(contrasena)
    query = (
        "INSERT INTO Cliente (documento, nombre, telefono, direccion, correo, "
        "contrasena, infracciones, id_licencia, id_tipo_documento, "
        "id_tipo_cliente, id_codigo_postal, id_cuenta) "
        "VALUES (%s, %s, %s, %s, %s, %s, 0, %s, %s, %s, %s, NULL)"
    )
    conexion = ConexionBD()
    conexion.ejecutar(
        query,
        (
            documento,
            nombre,
            telefono,
            direccion,
            correo,
            hashed,
            id_licencia,
            id_tipo_documento,
            id_tipo_cliente,
            id_codigo_postal,
        ),
    )
