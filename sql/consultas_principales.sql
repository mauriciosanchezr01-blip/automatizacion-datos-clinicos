-- =============================================================================
-- consultas_principales.sql
-- Proyecto: Automatización de Datos Clínicos
-- Autor: Mauricio Sánchez
-- Descripción: Consultas SQL para análisis de registros clínicos en PostgreSQL
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 1. CREACIÓN DE LA TABLA PRINCIPAL
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS registros_clinicos (
    id_registro             SERIAL PRIMARY KEY,
    id_paciente             VARCHAR(20)     NOT NULL,
    tipo_documento          VARCHAR(5)      NOT NULL,
    numero_documento        VARCHAR(20)     NOT NULL,
    fecha_nacimiento        DATE,
    sexo                    CHAR(1),
    codigo_servicio         VARCHAR(10),
    descripcion_servicio    VARCHAR(100),
    codigo_diagnostico      VARCHAR(10),
    descripcion_diagnostico VARCHAR(200),
    fecha_atencion          DATE,
    hora_atencion           TIME,
    valor_servicio          NUMERIC(12,2),
    codigo_medico           VARCHAR(20),
    codigo_ips              VARCHAR(20),
    municipio               VARCHAR(80),
    departamento            VARCHAR(80),
    estado_registro         VARCHAR(20)     DEFAULT 'PENDIENTE',
    fecha_cargue            TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);


-- -----------------------------------------------------------------------------
-- 2. INDICADORES DE CALIDAD DEL DATO
-- -----------------------------------------------------------------------------

-- Total de registros por estado de validación
SELECT
    estado_registro,
    COUNT(*)                                    AS total_registros,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS porcentaje
FROM registros_clinicos
GROUP BY estado_registro
ORDER BY total_registros DESC;


-- Registros con diagnóstico vacío
SELECT
    id_registro,
    id_paciente,
    fecha_atencion,
    codigo_servicio,
    descripcion_servicio
FROM registros_clinicos
WHERE codigo_diagnostico IS NULL
   OR TRIM(codigo_diagnostico) = ''
ORDER BY fecha_atencion DESC;


-- Registros con valor de servicio negativo o cero
SELECT
    id_registro,
    id_paciente,
    fecha_atencion,
    codigo_servicio,
    valor_servicio
FROM registros_clinicos
WHERE valor_servicio <= 0
   OR valor_servicio IS NULL
ORDER BY valor_servicio ASC;


-- Registros duplicados por paciente, fecha y servicio
SELECT
    id_paciente,
    fecha_atencion,
    codigo_servicio,
    COUNT(*) AS veces_repetido
FROM registros_clinicos
GROUP BY id_paciente, fecha_atencion, codigo_servicio
HAVING COUNT(*) > 1
ORDER BY veces_repetido DESC;


-- Porcentaje de completitud por campo obligatorio
SELECT
    'id_paciente'          AS campo, ROUND(COUNT(id_paciente) * 100.0 / COUNT(*), 2)          AS completitud_pct FROM registros_clinicos
UNION ALL SELECT
    'codigo_diagnostico',          ROUND(COUNT(codigo_diagnostico) * 100.0 / COUNT(*), 2)     FROM registros_clinicos
UNION ALL SELECT
    'codigo_servicio',             ROUND(COUNT(codigo_servicio) * 100.0 / COUNT(*), 2)        FROM registros_clinicos
UNION ALL SELECT
    'valor_servicio',              ROUND(COUNT(valor_servicio) * 100.0 / COUNT(*), 2)         FROM registros_clinicos
UNION ALL SELECT
    'codigo_medico',               ROUND(COUNT(codigo_medico) * 100.0 / COUNT(*), 2)          FROM registros_clinicos
ORDER BY completitud_pct ASC;


-- -----------------------------------------------------------------------------
-- 3. INDICADORES OPERATIVOS
-- -----------------------------------------------------------------------------

-- Producción total por tipo de servicio
SELECT
    codigo_servicio,
    descripcion_servicio,
    COUNT(*)                        AS total_atenciones,
    COUNT(DISTINCT id_paciente)     AS pacientes_unicos,
    SUM(valor_servicio)             AS valor_total_cop,
    ROUND(AVG(valor_servicio), 2)   AS valor_promedio_cop
FROM registros_clinicos
WHERE estado_registro != 'RECHAZADO'
GROUP BY codigo_servicio, descripcion_servicio
ORDER BY total_atenciones DESC;


-- Top 10 diagnósticos más frecuentes
SELECT
    codigo_diagnostico,
    descripcion_diagnostico,
    COUNT(*)                        AS frecuencia,
    COUNT(DISTINCT id_paciente)     AS pacientes_unicos,
    ROUND(AVG(valor_servicio), 2)   AS valor_promedio_cop
FROM registros_clinicos
WHERE codigo_diagnostico IS NOT NULL
  AND TRIM(codigo_diagnostico) != ''
  AND estado_registro != 'RECHAZADO'
GROUP BY codigo_diagnostico, descripcion_diagnostico
ORDER BY frecuencia DESC
LIMIT 10;


-- Producción por IPS y municipio
SELECT
    codigo_ips,
    municipio,
    departamento,
    COUNT(*)                        AS total_atenciones,
    COUNT(DISTINCT id_paciente)     AS pacientes_unicos,
    SUM(valor_servicio)             AS valor_total_cop,
    ROUND(AVG(valor_servicio), 2)   AS valor_promedio_cop
FROM registros_clinicos
WHERE estado_registro != 'RECHAZADO'
GROUP BY codigo_ips, municipio, departamento
ORDER BY total_atenciones DESC;


-- -----------------------------------------------------------------------------
-- 4. ANÁLISIS DEMOGRÁFICO
-- -----------------------------------------------------------------------------

-- Distribución por sexo
SELECT
    sexo,
    COUNT(*)                                            AS total_atenciones,
    COUNT(DISTINCT id_paciente)                         AS pacientes_unicos,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2)  AS porcentaje
FROM registros_clinicos
WHERE estado_registro != 'RECHAZADO'
GROUP BY sexo
ORDER BY total_atenciones DESC;


-- Distribución por grupo etario
SELECT
    CASE
        WHEN EXTRACT(YEAR FROM AGE(fecha_atencion, fecha_nacimiento)) < 1   THEN 'Menor de 1 año'
        WHEN EXTRACT(YEAR FROM AGE(fecha_atencion, fecha_nacimiento)) < 5   THEN '1 a 4 años'
        WHEN EXTRACT(YEAR FROM AGE(fecha_atencion, fecha_nacimiento)) < 15  THEN '5 a 14 años'
        WHEN EXTRACT(YEAR FROM AGE(fecha_atencion, fecha_nacimiento)) < 30  THEN '15 a 29 años'
        WHEN EXTRACT(YEAR FROM AGE(fecha_atencion, fecha_nacimiento)) < 45  THEN '30 a 44 años'
        WHEN EXTRACT(YEAR FROM AGE(fecha_atencion, fecha_nacimiento)) < 60  THEN '45 a 59 años'
        ELSE '60 años y más'
    END                                                 AS grupo_etario,
    COUNT(*)                                            AS total_atenciones,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2)  AS porcentaje
FROM registros_clinicos
WHERE fecha_nacimiento IS NOT NULL
  AND estado_registro != 'RECHAZADO'
GROUP BY grupo_etario
ORDER BY total_atenciones DESC;


-- -----------------------------------------------------------------------------
-- 5. ANÁLISIS TEMPORAL
-- -----------------------------------------------------------------------------

-- Evolución mensual de atenciones y facturación
SELECT
    TO_CHAR(fecha_atencion, 'YYYY-MM')          AS periodo,
    COUNT(*)                                    AS total_atenciones,
    COUNT(DISTINCT id_paciente)                 AS pacientes_unicos,
    SUM(valor_servicio)                         AS valor_total_cop,
    ROUND(AVG(valor_servicio), 2)               AS valor_promedio_cop
FROM registros_clinicos
WHERE estado_registro != 'RECHAZADO'
  AND fecha_atencion IS NOT NULL
GROUP BY periodo
ORDER BY periodo ASC;


-- Atenciones por día de la semana
SELECT
    TO_CHAR(fecha_atencion, 'Day')              AS dia_semana,
    EXTRACT(DOW FROM fecha_atencion)            AS numero_dia,
    COUNT(*)                                    AS total_atenciones,
    ROUND(AVG(valor_servicio), 2)               AS valor_promedio_cop
FROM registros_clinicos
WHERE estado_registro != 'RECHAZADO'
  AND fecha_atencion IS NOT NULL
GROUP BY dia_semana, numero_dia
ORDER BY numero_dia ASC;


-- -----------------------------------------------------------------------------
-- 6. VISTA RESUMEN PARA POWER BI
-- -----------------------------------------------------------------------------

CREATE OR REPLACE VIEW vw_registros_analitica AS
SELECT
    rc.id_registro,
    rc.id_paciente,
    rc.tipo_documento,
    rc.sexo,
    rc.codigo_servicio,
    rc.descripcion_servicio,
    rc.codigo_diagnostico,
    rc.descripcion_diagnostico,
    rc.fecha_atencion,
    rc.valor_servicio,
    rc.codigo_ips,
    rc.municipio,
    rc.departamento,
    rc.estado_registro,
    TO_CHAR(rc.fecha_atencion, 'YYYY-MM')       AS periodo,
    EXTRACT(YEAR FROM rc.fecha_atencion)        AS anio,
    EXTRACT(MONTH FROM rc.fecha_atencion)       AS mes,
    EXTRACT(YEAR FROM AGE(rc.fecha_atencion, rc.fecha_nacimiento)) AS edad_anos,
    CASE
        WHEN EXTRACT(YEAR FROM AGE(rc.fecha_atencion, rc.fecha_nacimiento)) < 15  THEN 'Menor de 15 años'
        WHEN EXTRACT(YEAR FROM AGE(rc.fecha_atencion, rc.fecha_nacimiento)) < 30  THEN '15 a 29 años'
        WHEN EXTRACT(YEAR FROM AGE(rc.fecha_atencion, rc.fecha_nacimiento)) < 45  THEN '30 a 44 años'
        WHEN EXTRACT(YEAR FROM AGE(rc.fecha_atencion, rc.fecha_nacimiento)) < 60  THEN '45 a 59 años'
        ELSE '60 años y más'
    END AS grupo_etario
FROM registros_clinicos rc
WHERE rc.estado_registro != 'RECHAZADO';
