# 🏥 Automatización de Datos Clínicos

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![SQL](https://img.shields.io/badge/SQL-PostgreSQL-336791?style=flat-square&logo=postgresql)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?style=flat-square&logo=powerbi)
![Estado](https://img.shields.io/badge/Estado-En%20desarrollo-green?style=flat-square)
![Licencia](https://img.shields.io/badge/Licencia-MIT-lightgrey?style=flat-square)

> Pipeline automatizado de validación, limpieza y análisis de registros clínicos para IPS colombianas.  
> Reduce errores de facturación, detecta inconsistencias antes de la radicación y genera reportes ejecutivos automáticos.

---

## 📌 Problema que resuelve

Las IPS en Colombia enfrentan pérdidas económicas significativas por glosas originadas en errores en los registros de prestación de servicios. El proceso manual de revisión es lento, propenso a errores humanos y no escala con el volumen de atenciones.

Este proyecto automatiza ese proceso: desde la recepción del archivo plano hasta la generación de un reporte ejecutivo con los hallazgos críticos.

---

## 🎯 Objetivo del proyecto

Construir un pipeline en Python y SQL que permita a una IPS:

- Validar la estructura y contenido de los registros clínicos según la normativa vigente
- Detectar y clasificar errores antes de la radicación ante el pagador
- Calcular indicadores clave de calidad del dato
- Generar reportes automáticos en Excel y visualizaciones en Power BI

---

## 📁 Estructura del proyecto

```
automatizacion-datos-clinicos/
│
├── data/
│   ├── raw/               # Archivos fuente sin modificar
│   └── processed/         # Datos limpios y transformados
│
├── notebooks/
│   └── 01_exploracion.ipynb
│
├── src/
│   ├── validacion.py
│   ├── limpieza.py
│   ├── indicadores.py
│   └── reporte.py
│
├── sql/
│   └── consultas_principales.sql
│
├── dashboard/
│   └── README.md
│
├── docs/
│   └── diccionario_datos.md
│
├── .gitignore
├── requirements.txt
└── README.md
```

## ⚙️ Tecnologías utilizadas

| Herramienta | Uso |
|-------------|-----|
| Python 3.10+ | Procesamiento, validación y automatización |
| Pandas / NumPy | Transformación y análisis de datos |
| PostgreSQL | Almacenamiento y consultas relacionales |
| Power BI + DAX | Visualización ejecutiva |
| Excel (openpyxl) | Reportes automáticos exportables |
| Git / GitHub | Control de versiones y documentación |

---

## 📊 Indicadores que genera el pipeline

| Indicador | Descripción |
|-----------|-------------|
| Tasa de error por campo | % de registros con inconsistencias por variable |
| Registros sin diagnóstico | Atenciones sin código CIE-10 válido |
| Inconsistencias de fecha | Fechas de atención fuera de rango o incoherentes |
| Duplicados detectados | Registros con mismo paciente, fecha y servicio |
| Cobertura de datos | % de campos obligatorios correctamente diligenciados |

---

## 🗂️ Contexto normativo

Este proyecto toma como referencia el marco normativo del Sistema General de Seguridad Social en Salud (SGSSS) de Colombia:

- Resolución 3374 de 2000 — estructura de registros individuales de prestación de servicios
- Circular 056 de 2009 SUPERSALUD — calidad del dato en facturación
- Resolución 2275 de 2023 — actualización de estándares de interoperabilidad en salud

---

## 🚀 Cómo ejecutar el proyecto

```bash
# 1. Clonar el repositorio
git clone https://github.com/mauriciosanchezr01-blip/automatizacion-datos-clinicos.git

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar el pipeline completo
python src/validacion.py
python src/limpieza.py
python src/indicadores.py
python src/reporte.py
```

---

## 📈 Resultados esperados

- Reducción del tiempo de revisión manual en un 70%
- Detección temprana de errores que generan glosas
- Reporte ejecutivo listo para presentar a gerencia o al área de facturación
- Base de datos limpia y estructurada para análisis posteriores

---

## ⚠️ Aviso de privacidad

Todos los datos utilizados en este proyecto son **ficticios y generados sintéticamente**.  
No contienen información real de pacientes ni de instituciones de salud.  
Este proyecto cumple con los principios de la **Ley 1581 de 2012 — Habeas Data** de Colombia.

---

## 👤 Autor

**Mauricio Sánchez**  
Analista de Datos en Salud | Especialista en Ciencia de Datos  
Estudiante de Maestría en TIC en Salud — Universidad CES  
📍 Medellín, Antioquia, Colombia  
🔗 [GitHub](https://github.com/mauriciosanchezr01-blip)

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.
