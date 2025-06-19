USE alquiler_vehiculos;

-- Tipos de empleado
INSERT INTO tipo_empleado (nombre, descripcion) VALUES
    ('empleado', 'Empleado regular'),
    ('gerente', 'Gerente de sucursal'),
    ('admin', 'Administrador del sistema');

-- Clientes con correos únicos
INSERT INTO clientes (nombre, documento, telefono, direccion, correo, contrasena) VALUES
    ('Ana García', '1010', '3000000001', 'Calle 1', 'cliente1@correo.com', SHA2('cliente123',256)),
    ('Luis Pérez', '2020', '3000000002', 'Calle 2', 'cliente2@correo.com', SHA2('cliente123',256)),
    ('María Rodríguez', '3030', '3000000003', 'Calle 3', 'cliente3@correo.com', SHA2('cliente123',256));

-- Empleados de diferentes tipos
INSERT INTO empleados (nombre, documento, telefono, direccion, correo, contrasena, tipo_empleado_id) VALUES
    ('Carlos Gómez', '4040', '3100000001', 'Cra 1', 'empleado1@empresa.com', SHA2('empleado123',256), 1),
    ('Laura Méndez', '5050', '3100000002', 'Cra 2', 'gerente1@empresa.com', SHA2('gerente123',256), 2),
    ('Administrador', '6060', '3100000003', 'Cra 3', 'admin@admin.com', SHA2('admin123',256), 3);
