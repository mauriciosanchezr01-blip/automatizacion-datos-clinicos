# 📖 Diccionario de Datos

## Tabla: registros_clinicos

| Variable | Tipo | Descripción | Ejemplo | Obligatorio |
|----------|------|-------------|---------|-------------|
| id_registro | Entero | Identificador único del registro | 1 | Sí |
| id_paciente | Texto | Código interno del paciente en la IPS | PAC001 | Sí |
| tipo_documento | Texto | Tipo de documento de identidad (CC, TI, CE, PA, RC) | CC | Sí |
| numero_documento | Texto | Número del documento de identidad | 10234567 | Sí |
| fecha_nacimiento | Fecha | Fecha de nacimiento del paciente (YYYY-MM-DD) | 1985-03-12 | Sí |
| sexo | Texto | Sexo biológico del paciente (M: Masculino, F: Femenino) | M | Sí |
| codigo_servicio | Texto | Código del servicio prestado según CUPS | 890301 | Sí |
| descripcion_servicio | Texto | Descripción del servicio prestado | Consulta médica general | Sí |
| codigo_diagnostico | Texto | Código del diagnóstico según CIE-10 | J06.9 | Sí |
| descripcion_diagnostico | Texto | Descripción del diagnóstico CIE-10 | Infección aguda vías respiratorias | Sí |
| fecha_atencion | Fecha | Fecha en que se prestó el servicio (YYYY-MM-DD) | 2024-01-15 | Sí |
| hora_atencion | Hora | Hora en que se prestó el servicio (HH:MM) | 08:30 | No |
| valor_servicio | Decimal | Valor en pesos colombianos del servicio prestado | 35000 | Sí |
| codigo_medico | Texto | Código del profesional de salud que atendió | MED001 | Sí |
| codigo_ips | Texto | Código de la IPS que prestó el servicio | IPS001 | Sí |
| municipio | Texto | Municipio donde se prestó el servicio | Medellín | Sí |
| departamento | Texto | Departamento donde se prestó el servicio | Antioquia | Sí |

---

## Estados de validación

| Estado | Descripción |
|--------|-------------|
| VÁLIDO | Registro sin errores, apto para radicación |
| ADVERTENCIA | Registro con un error menor, requiere revisión |
| RECHAZADO | Registro con dos o más errores, no apto para radicación |

---

## Tipos de error detectados por el pipeline

| Código de error | Descripción |
|-----------------|-------------|
| error_tipo_documento | El tipo de documento no corresponde a los permitidos |
| error_sexo | El sexo registrado no es M ni F |
| error_fecha_atencion | La fecha de atención tiene formato incorrecto o está fuera de rango |
| error_fecha_nacimiento | La fecha de nacimiento tiene formato incorrecto |
| error_valor_negativo | El valor del servicio es negativo o cero |
| error_duplicado | El registro aparece más de una vez con el mismo paciente, fecha y servicio |
| error_diagnostico_vacio | El código de diagnóstico está vacío |

---

## Fuentes normativas

| Norma | Descripción |
|-------|-------------|
| Resolución 3374 de 2000 | Define la estructura de los registros individuales de prestación de servicios de salud |
| Circular 056 de 2009 | Establece estándares de calidad del dato en facturación — Supersalud |
| Resolución 2275 de 2023 | Actualiza los estándares de interoperabilidad en salud en Colombia |
| CIE-10 | Clasificación Internacional de Enfermedades, décima revisión — OMS |
| CUPS | Clasificación Única de Procedimientos en Salud — Ministerio de Salud Colombia |

---

## Notas

- Todos los datos de este proyecto son registros de prueba creados por el autor.
- No contienen información real de pacientes ni de instituciones de salud.
- Este proyecto cumple con los principios de la Ley 1581 de 2012 — Habeas Data de Colombia.
