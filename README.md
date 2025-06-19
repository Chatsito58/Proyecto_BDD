# Sistema de Gestión de Alquiler de Vehículos

Este proyecto es un ejemplo académico para la materia Bases de Datos Distribuidas.
Incluye una aplicación en Python con autenticación por roles y soporte para bases
MySQL con tolerancia a fallos.

## Requisitos
- Python 3.10+
- MySQL Server
- Dependencias indicadas en `requirements.txt` (instalar con `pip install -r requirements.txt`)

## Instalación
1. Crear un entorno virtual y activar.
2. Copiar el archivo `.env` y configurar las variables:
   - `DB1_HOST`, `DB1_USER`, `DB1_PASSWORD`, `DB1_NAME`
   - `DB2_HOST`, `DB2_USER`, `DB2_PASSWORD`, `DB2_NAME`
   - `GOOGLE_MAPS_API_KEY` y `TWILIO_API_KEY`
3. Ejecutar los scripts de `scripts/` en la base local y remota:
   ```bash
   mysql -u root -p < scripts/crear_bd.sql
   mysql -u root -p alquiler_vehiculos < scripts/poblar_bd.sql
   ```

## Uso
Ejecutar `python main.py` para iniciar la interfaz de login. Según el rol del
usuario se mostrará la ventana correspondiente. Todas las ventanas incluyen la
opción de cerrar sesión.

## Pruebas
El directorio `tests` contiene `simular_falla.py` para probar el cambio de base
en caso de fallo:
```bash
python tests/simular_falla.py
```
