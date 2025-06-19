-- Script de creación de base de datos
DROP DATABASE IF EXISTS alquiler_vehiculos;
CREATE DATABASE alquiler_vehiculos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE alquiler_vehiculos;

-- Tabla de tipos de empleado
CREATE TABLE tipo_empleado (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT
) ENGINE=InnoDB;

-- Tabla de clientes
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    documento VARCHAR(20) NOT NULL,
    telefono VARCHAR(20),
    direccion VARCHAR(255),
    correo VARCHAR(100) NOT NULL UNIQUE,
    contrasena CHAR(64) NOT NULL
) ENGINE=InnoDB;

-- Tabla de empleados
CREATE TABLE empleados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    documento VARCHAR(20) NOT NULL,
    telefono VARCHAR(20),
    direccion VARCHAR(255),
    correo VARCHAR(100) NOT NULL UNIQUE,
    contrasena CHAR(64) NOT NULL,
    tipo_empleado_id INT NOT NULL,
    FOREIGN KEY (tipo_empleado_id) REFERENCES tipo_empleado(id)
) ENGINE=InnoDB;
