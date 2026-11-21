CREATE DATABASE IF NOT EXISTS etl_bi
CHARACTER SET utf8mb4;

USE etl_bi;

CREATE TABLE IF NOT EXISTS violencia_homicida (
    codigo_provincia CHAR(2) NOT NULL,
    provincia VARCHAR(50) NOT NULL,
    anio SMALLINT NOT NULL,
    poblacion INT NOT NULL,
    homicidios INT NULL,
    estado_registro VARCHAR(20) NOT NULL,
    tasa_homicidios_100mil DECIMAL(10,2) NULL,

    PRIMARY KEY (codigo_provincia, anio)
);