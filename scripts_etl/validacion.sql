-- PROYECTO ETL_BI
-- VALIDACIÓN DEL CONJUNTO DE DATOS INTEGRADO

-- 1. Visualización del conjunto de datos almacenado.
-- Permite consultar los registros ordenados por provincia y año.

SELECT *
FROM violencia_homicida
ORDER BY codigo_provincia, anio;


-- 2. Validación de la cantidad de registros.
-- Resultado esperado: 48 registros.

SELECT COUNT(*) AS total_registros
FROM violencia_homicida;


-- 3. Validación de la cobertura provincial.
-- Comprueba la existencia de las 24 provincias en cada año.

SELECT
    anio,
    COUNT(DISTINCT codigo_provincia) AS total_provincias
FROM violencia_homicida
GROUP BY anio
ORDER BY anio;


-- 4. Validación de los totales de homicidios.
-- Comprueba que los valores coincidan con la transformación.
-- Resultados esperados: 7621 en 2025 y 6889 en 2026.

SELECT
    anio,
    SUM(homicidios) AS total_homicidios
FROM violencia_homicida
GROUP BY anio
ORDER BY anio;


-- 5. Validación de registros sin correspondencia.
-- Identifica las provincias sin registros de homicidios.
-- Resultado esperado: dos registros de Galápagos.

SELECT
    codigo_provincia,
    provincia,
    anio,
    homicidios,
    estado_registro
FROM violencia_homicida
WHERE estado_registro = 'SIN_REGISTROS';


-- 6. Validación de claves duplicadas.
-- Comprueba que cada combinación de provincia y año sea única.
-- Resultado esperado: ningún registro.

SELECT
    codigo_provincia,
    anio,
    COUNT(*) AS cantidad
FROM violencia_homicida
GROUP BY codigo_provincia, anio
HAVING COUNT(*) > 1;


-- 7. Validación de valores poblacionales.
-- Comprueba que la población sea mayor que cero.
-- Resultado esperado: ningún registro.

SELECT *
FROM violencia_homicida
WHERE poblacion <= 0 OR poblacion IS NULL;


-- 8. Validación del cálculo de la tasa de homicidios.
-- Compara la tasa almacenada con la calculada mediante SQL.
-- Resultado esperado: ningún registro con diferencias.

SELECT
    provincia,
    anio,
    tasa_homicidios_100mil AS tasa_almacenada,
    ROUND(homicidios * 100000.0 / poblacion, 2)
        AS tasa_calculada
FROM violencia_homicida
WHERE homicidios IS NOT NULL
AND NOT (
    tasa_homicidios_100mil <=>
    ROUND(homicidios * 100000.0 / poblacion, 2)
);


-- 9. Validación del estado de los registros.
-- Comprueba que los valores faltantes sean coherentes
-- con el estado asignado durante la integración.
-- Resultado esperado: ningún registro inconsistente.

SELECT *
FROM violencia_homicida
WHERE
    (
        estado_registro = 'SIN_REGISTROS'
        AND (homicidios IS NOT NULL
             OR tasa_homicidios_100mil IS NOT NULL)
    )
    OR
    (
        estado_registro = 'DISPONIBLE'
        AND (homicidios IS NULL
             OR tasa_homicidios_100mil IS NULL)
    )
    OR estado_registro NOT IN ('DISPONIBLE', 'SIN_REGISTROS');

   

















   
-- ============================================
-- CONSULTA DE LA NECESIDAD DE INFORMACIÓN
-- Comparación provincial de homicidios 2025-2026
-- Periodo: enero - octubre
-- ============================================

WITH comparacion AS (

    SELECT
        codigo_provincia,
        provincia,

        MAX(CASE WHEN anio = 2025
            THEN homicidios END) AS homicidios_2025,

        MAX(CASE WHEN anio = 2026
            THEN homicidios END) AS homicidios_2026,

        MAX(CASE WHEN anio = 2025
            THEN tasa_homicidios_100mil END) AS tasa_2025,

        MAX(CASE WHEN anio = 2026
            THEN tasa_homicidios_100mil END) AS tasa_2026

    FROM violencia_homicida

    GROUP BY codigo_provincia, provincia
)

SELECT
    provincia,
    homicidios_2025,
    homicidios_2026,

    homicidios_2026 - homicidios_2025 AS variacion,

    ROUND(
        (homicidios_2026 - homicidios_2025)
        * 100.0 / NULLIF(homicidios_2025, 0), 2
    ) AS variacion_porcentual,

    tasa_2025,
    tasa_2026,

    CASE
        WHEN homicidios_2025 IS NULL
          OR homicidios_2026 IS NULL
            THEN 'SIN DATOS SUFICIENTES'

        WHEN homicidios_2026 > homicidios_2025
            THEN 'AUMENTO'

        WHEN homicidios_2026 < homicidios_2025
            THEN 'DISMINUCION'

        ELSE 'SIN CAMBIO'
    END AS tendencia

FROM comparacion
ORDER BY variacion DESC;