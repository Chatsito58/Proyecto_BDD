DROP DATABASE remota_alquiler_vehiculos;
CREATE DATABASE IF NOT EXISTS remota_alquiler_vehiculos;
USE remota_alquiler_vehiculos;
CREATE TABLE Remota_Tipo_entidad (
  id_tipo_entidad   INT,
  descripcion       VARCHAR(100) 
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Tipo_entidad';

CREATE TABLE Remota_Medio_pago (
  id_medio_pago     INT,
  descripcion       VARCHAR(100) 
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Medio_pago';

CREATE TABLE Remota_Tipo_cliente (
  id_tipo           INT,
  descripcion       VARCHAR(100) 
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Tipo_cliente';

CREATE TABLE Remota_Tipo_documento (
  id_tipo_documento INT,
  descripcion       VARCHAR(100) 
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Tipo_documento';

CREATE TABLE Remota_Codigo_postal (
  id_codigo_postal  VARCHAR(50) ,
  pais              VARCHAR(50) ,
  departamento      VARCHAR(50) ,
  ciudad            VARCHAR(50) 
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Codigo_postal';

CREATE TABLE Remota_Categoria_licencia (
  id_categoria      INT,
  descripcion       VARCHAR(100) 
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Categoria_licencia';

CREATE TABLE Remota_Tipo_mantenimiento (
  id_tipo           INT,
  descripcion       VARCHAR(100) 
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Tipo_mantenimiento';

CREATE TABLE Remota_Taller_mantenimiento (
  id_taller         INT,
  nombre            VARCHAR(100) ,
  direccion         VARCHAR(150),
  telefono          VARCHAR(20)
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Taller_mantenimiento';

CREATE TABLE Remota_Estado_vehiculo (
  id_estado         INT,
  descripcion       VARCHAR(100) 
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Estado_vehiculo';

CREATE TABLE Remota_Marca_vehiculo (
  id_marca          INT,
  nombre_marca      VARCHAR(100) 
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Marca_vehiculo';

CREATE TABLE Remota_Color_vehiculo (
  id_color          INT,
  nombre_color      VARCHAR(50) 
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Color_vehiculo';

CREATE TABLE Remota_Tipo_vehiculo (
  id_tipo           INT,
  descripcion       VARCHAR(100) ,
  capacidad         INT,
  combustible       VARCHAR(50),
  tarifa_dia        DECIMAL(10,2)
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Tipo_vehiculo';

CREATE TABLE Remota_Blindaje_vehiculo (
  id_blindaje       INT,
  descripcion       VARCHAR(100) 
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Blindaje_vehiculo';

CREATE TABLE Remota_Transmision_vehiculo (
  id_transmision    INT,
  descripcion       VARCHAR(50) 
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Transmision_vehiculo';

CREATE TABLE Remota_Cilindraje_vehiculo (
  id_cilindraje     INT,
  descripcion       VARCHAR(50) 
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Cilindraje_vehiculo';

CREATE TABLE Remota_Estado_alquiler (
  id_estado         INT,
  descripcion       VARCHAR(100) 
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Estado_alquiler';

-- Tabla de roles para empleados
CREATE TABLE Remota_Tipo_empleado (
  id_tipo_empleado INT,
  nombre VARCHAR(50) ,
  descripcion TEXT,
  permisos JSON 
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Tipo_empleado';


-- ------------------------------------------------------------------
-- 2) TABLAS PRINCIPALES / TRANSACCIONALES
-- ------------------------------------------------------------------

CREATE TABLE Remota_Sucursal (
  id_sucursal       INT,
  nombre            VARCHAR(100),
  direccion         VARCHAR(150),
  telefono          VARCHAR(20),
  gerente           VARCHAR(100),
  id_codigo_postal  VARCHAR(50)
  ) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Sucursal';

CREATE TABLE Remota_Empleado (
  id_empleado       INT,
  documento         VARCHAR(20),
  nombre            VARCHAR(100),
  salario           DECIMAL(10,2),
  cargo             VARCHAR(100),
  telefono          VARCHAR(20),
  direccion         VARCHAR(150),
  correo            VARCHAR(100),
  contrasena        CHAR(64),
  id_tipo_empleado  INT,
  id_tipo_documento INT
  ) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Empleado';

CREATE TABLE Remota_Licencia_conduccion (
  id_licencia       INT,
  estado            VARCHAR(20),
  fecha_emision     DATE,
  fecha_vencimiento DATE,
  id_categoria      INT
  ) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Licencia_conduccion';

CREATE TABLE Remota_Cliente (
  id_cliente        INT,
  documento         VARCHAR(20) ,
  nombre            VARCHAR(100) ,
  telefono          VARCHAR(20),
  direccion         VARCHAR(150),
  correo            VARCHAR(100)  ,
  contrasena        CHAR(64) ,
  infracciones      INT ,
  id_licencia       INT,
  id_tipo_documento INT,
  id_tipo_cliente   INT,
  id_codigo_postal  VARCHAR(50),
  id_cuenta         INT
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Cliente';

CREATE TABLE Remota_Seguro_vehiculo (
  id_seguro         INT,
  estado            VARCHAR(50),
  descripcion       VARCHAR(255),
  vencimiento       DATE,
  costo             DECIMAL(10,2)
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Seguro_vehiculo';

CREATE TABLE Remota_Proveedor_vehiculo (
  id_proveedor      INT,
  nombre            VARCHAR(100),
  direccion         VARCHAR(150),
  telefono          VARCHAR(20),
  correo            VARCHAR(100),
  id_cuenta         INT
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Proveedor_vehiculo';

CREATE TABLE Remota_Mantenimiento_vehiculo (
  id_mantenimiento  INT,
  descripcion       VARCHAR(255),
  fecha_hora        DATETIME,
  valor             DECIMAL(10,2),
  id_tipo           INT,
  id_taller         INT,
  id_vehiculo       VARCHAR(20)
  
  ) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Mantenimiento_vehiculo';

-- Crear tabla Vehiculo
CREATE TABLE Remota_Vehiculo (
  placa              VARCHAR(20),
  n_chasis           VARCHAR(50),
  modelo             VARCHAR(50),
  kilometraje        INT,
  id_marca           INT,
  id_color           INT,
  id_tipo_vehiculo   INT,
  id_blindaje        INT,
  id_transmision     INT,
  id_cilindraje      INT,
  id_seguro_vehiculo INT,
  id_estado_vehiculo INT,
  id_proveedor       INT,
  id_sucursal        INT
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Vehiculo';

CREATE TABLE Remota_Descuento_alquiler (
  id_descuento      INT,
  descripcion       VARCHAR(255),
  valor             DECIMAL(10,2)
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Descuento_alquiler';

CREATE TABLE Remota_Estado_reserva (
  id_estado         INT,
  descripcion       VARCHAR(100)
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Estado_reserva';

CREATE TABLE Remota_Seguro_alquiler (
  id_seguro         INT,
  estado            VARCHAR(50),
  descripcion       VARCHAR(255),
  vencimiento       DATE,
  costo             DECIMAL(10,2)
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Seguro_alquiler';

-- Crear tabla Reserva_alquiler sin la columna id_alquiler
CREATE TABLE Remota_Reserva_alquiler (
  id_reserva         INT,
  fecha_hora         DATETIME,
  fecha_hora_salida  DATETIME,
  fecha_hora_entrada DATETIME,
  abono              DECIMAL(10,2),
  saldo_pendiente    DECIMAL(10,2),
  id_cliente         INT,
  id_estado_reserva  INT
  ) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Reserva_alquiler';

-- Crear tabla Alquiler
CREATE TABLE Remota_Alquiler (
  id_alquiler        INT,
  fecha_hora_salida  DATETIME,
  valor              DECIMAL(10,2),
  fecha_hora_entrada DATETIME,
  id_vehiculo        VARCHAR(20),
  id_cliente         INT,
  id_sucursal        INT,
  id_medio_pago      INT,
  id_estado          INT,
  id_seguro          INT,
  id_descuento       INT
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Alquiler';

CREATE TABLE Remota_Det_factura (
  id_det_factura    INT,
  id_servicio       INT,
  valor             DECIMAL(10,2),
  impuestos         DECIMAL(10,2)
) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Det_factura';

CREATE TABLE Remota_Factura (
  id_factura        INT,
  valor             DECIMAL(10,2),
  id_alquiler       INT,
  id_cliente        INT,
  id_vehiculo       VARCHAR(20),
  id_det_factura    INT  
  ) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Factura';

CREATE TABLE Remota_Cuenta_pagar (
  id_cuenta_pagar   INT,
  fecha_hora        DATETIME,
  valor             DECIMAL(10,2),
  descripcion       VARCHAR(255),
  id_medio_pago     INT,
  id_tipo_entidad   INT,
  id_entidad        INT  
  ) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Cuenta_pagar';

CREATE TABLE Remota_Cuenta_cobrar (
  id_cuenta_cobrar  INT,
  fecha_hora        DATETIME,
  valor             DECIMAL(10,2),
  descripcion       VARCHAR(255),
  id_medio_pago     INT,
  id_tipo_entidad   INT,
  id_entidad        INT
  ) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Cuenta_cobrar';

CREATE TABLE Remota_Cuenta (
  id_cuenta         INT,
  id_cuenta_pagar   INT,
  id_cuenta_cobrar  INT  
  ) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Cuenta';

CREATE TABLE Remota_Abono_reserva (
  id_abono          INT,
  valor             DECIMAL(10,2),
  fecha_hora        DATETIME,
  id_reserva        INT,
  id_medio_pago     INT  
  ) ENGINE=FEDERATED
CONNECTION='mysql://alquiler:12345@192.168.230.200:3306/alquiler_vehiculos/Abono_reserva';

