# =============================================================================
# reporte.py
# Proyecto: Automatización de Datos Clínicos
# Autor: Mauricio Sánchez
# Descripción: Generación automática de reporte ejecutivo en Excel
# =============================================================================

import pandas as pd
import numpy as np
import os
from datetime import datetime

# -----------------------------------------------------------------------------
# CONFIGURACIÓN
# -----------------------------------------------------------------------------

RUTA_LIMPIOS      = "data/processed/registros_limpios.csv"
RUTA_VALIDADOS    = "data/processed/registros_validados.csv"
RUTA_INDICADORES  = "data/processed/indicadores_resumen.csv"
RUTA_REPORTE      = "data/processed/reporte_ejecutivo.xlsx"


# -----------------------------------------------------------------------------
# CARGA DE DATOS
# -----------------------------------------------------------------------------

def cargar_datos() -> tuple:
    """Carga los archivos procesados del pipeline."""
    df_limpios = pd.read_csv(RUTA_LIMPIOS, encoding="utf-8")
    df_limpios["fecha_atencion"]   = pd.to_datetime(df_limpios["fecha_atencion"],   errors="coerce")
    df_limpios["fecha_nacimiento"] = pd.to_datetime(df_limpios["fecha_nacimiento"], errors="coerce")
    df_limpios["valor_servicio"]   = pd.to_numeric(df_limpios["valor_servicio"],    errors="coerce")

    df_validados = pd.read_csv(RUTA_VALIDADOS, encoding="utf-8")

    print(f"Registros limpios cargados   : {len(df_limpios)}")
    print(f"Registros validados cargados : {len(df_validados)}")
    return df_limpios, df_validados


# -----------------------------------------------------------------------------
# CONSTRUCCIÓN DE HOJAS DEL REPORTE
# -----------------------------------------------------------------------------

def hoja_resumen_ejecutivo(df_limpios: pd.DataFrame, df_validados: pd.DataFrame) -> pd.DataFrame:
    """Genera la hoja de resumen ejecutivo con KPIs principales."""
    total_registros   = len(df_validados)
    validos           = (df_validados["estado_registro"] == "VÁLIDO").sum()    if "estado_registro" in df_validados.columns else 0
    advertencias      = (df_validados["estado_registro"] == "ADVERTENCIA").sum() if "estado_registro" in df_validados.columns else 0
    rechazados        = (df_validados["estado_registro"] == "RECHAZADO").sum()  if "estado_registro" in df_validados.columns else 0

    datos = {
        "Indicador": [
            "Total registros procesados",
            "Registros válidos",
            "Registros con advertencia",
            "Registros rechazados",
            "Tasa de calidad del dato (%)",
            "Pacientes únicos atendidos",
            "IPS registradas",
            "Municipios cubiertos",
            "Valor total facturado (COP)",
            "Valor promedio por atención (COP)",
            "Diagnóstico más frecuente",
            "Servicio más demandado",
            "Fecha de generación del reporte"
        ],
        "Valor": [
            total_registros,
            int(validos),
            int(advertencias),
            int(rechazados),
            round((validos / total_registros * 100), 2) if total_registros > 0 else 0,
            df_limpios["id_paciente"].nunique(),
            df_limpios["codigo_ips"].nunique(),
            df_limpios["municipio"].nunique(),
            f"$ {df_limpios['valor_servicio'].sum():,.0f}",
            f"$ {df_limpios['valor_servicio'].mean():,.0f}",
            df_limpios["codigo_diagnostico"].value_counts().idxmax() if len(df_limpios) > 0 else "N/A",
            df_limpios["descripcion_servicio"].value_counts().idxmax() if len(df_limpios) > 0 else "N/A",
            datetime.today().strftime("%Y-%m-%d %H:%M")
        ]
    }
    return pd.DataFrame(datos)


def hoja_produccion_servicios(df: pd.DataFrame) -> pd.DataFrame:
    """Producción por tipo de servicio."""
    return (
        df.groupby("descripcion_servicio")
        .agg(
            total_atenciones =("id_registro", "count"),
            pacientes_unicos =("id_paciente", "nunique"),
            valor_total_cop  =("valor_servicio", "sum"),
            valor_promedio   =("valor_servicio", "mean")
        )
        .round(2)
        .reset_index()
        .sort_values("total_atenciones", ascending=False)
        .rename(columns={
            "descripcion_servicio": "Tipo de servicio",
            "total_atenciones"    : "Total atenciones",
            "pacientes_unicos"    : "Pacientes únicos",
            "valor_total_cop"     : "Valor total (COP)",
            "valor_promedio"      : "Valor promedio (COP)"
        })
    )


def hoja_top_diagnosticos(df: pd.DataFrame) -> pd.DataFrame:
    """Top 10 diagnósticos más frecuentes."""
    return (
        df.groupby(["codigo_diagnostico", "descripcion_diagnostico"])
        .agg(
            frecuencia       =("id_registro", "count"),
            pacientes_unicos =("id_paciente", "nunique"),
            valor_total_cop  =("valor_servicio", "sum")
        )
        .reset_index()
        .sort_values("frecuencia", ascending=False)
        .head(10)
        .rename(columns={
            "codigo_diagnostico"      : "Código CIE-10",
            "descripcion_diagnostico" : "Diagnóstico",
            "frecuencia"              : "Frecuencia",
            "pacientes_unicos"        : "Pacientes únicos",
            "valor_total_cop"         : "Valor total (COP)"
        })
    )


def hoja_produccion_ips(df: pd.DataFrame) -> pd.DataFrame:
    """Producción por IPS y municipio."""
    return (
        df.groupby(["codigo_ips", "municipio", "departamento"])
        .agg(
            total_atenciones =("id_registro", "count"),
            pacientes_unicos =("id_paciente", "nunique"),
            valor_total_cop  =("valor_servicio", "sum")
        )
        .round(2)
        .reset_index()
        .sort_values("total_atenciones", ascending=False)
        .rename(columns={
            "codigo_ips"      : "Código IPS",
            "municipio"       : "Municipio",
            "departamento"    : "Departamento",
            "total_atenciones": "Total atenciones",
            "pacientes_unicos": "Pacientes únicos",
            "valor_total_cop" : "Valor total (COP)"
        })
    )


def hoja_distribucion_demografica(df: pd.DataFrame) -> pd.DataFrame:
    """Distribución de atenciones por sexo y grupo etario."""
    total = len(df)
    return (
        df.groupby(["sexo", "grupo_etario"])
        .agg(total_atenciones=("id_registro", "count"))
        .assign(porcentaje=lambda x: (x["total_atenciones"] / total * 100).round(2))
        .reset_index()
        .rename(columns={
            "sexo"            : "Sexo",
            "grupo_etario"    : "Grupo etario",
            "total_atenciones": "Total atenciones",
            "porcentaje"      : "Porcentaje (%)"
        })
    )


def hoja_evolucion_mensual(df: pd.DataFrame) -> pd.DataFrame:
    """Evolución mensual de atenciones y facturación."""
    return (
        df.groupby("periodo")
        .agg(
            total_atenciones =("id_registro", "count"),
            pacientes_unicos =("id_paciente", "nunique"),
            valor_total_cop  =("valor_servicio", "sum")
        )
        .round(2)
        .reset_index()
        .sort_values("periodo")
        .rename(columns={
            "periodo"         : "Período",
            "total_atenciones": "Total atenciones",
            "pacientes_unicos": "Pacientes únicos",
            "valor_total_cop" : "Valor total (COP)"
        })
    )


def hoja_registros_con_errores(df_validados: pd.DataFrame) -> pd.DataFrame:
    """Lista de registros con errores para revisión del equipo de facturación."""
    columnas_error = [c for c in df_validados.columns if c.startswith("error_")]
    df_errores = df_validados[df_validados["total_errores"] > 0].copy() if "total_errores" in df_validados.columns else pd.DataFrame()

    if len(df_errores) == 0:
        return pd.DataFrame({"Mensaje": ["No se encontraron registros con errores."]})

    columnas_base = [
        "id_registro", "id_paciente", "tipo_documento",
        "numero_documento", "fecha_atencion", "codigo_servicio",
        "codigo_diagnostico", "valor_servicio",
        "total_errores", "estado_registro"
    ]
    columnas_exportar = [c for c in columnas_base if c in df_errores.columns] + columnas_error
    return df_errores[columnas_exportar].rename(columns={"estado_registro": "Estado"})


# -----------------------------------------------------------------------------
# GENERACIÓN DEL ARCHIVO EXCEL
# -----------------------------------------------------------------------------

def generar_reporte_excel(df_limpios: pd.DataFrame, df_validados: pd.DataFrame) -> None:
    """Genera el reporte ejecutivo completo en Excel con múltiples hojas."""
    os.makedirs("data/processed", exist_ok=True)

    hojas = {
        "Resumen ejecutivo"       : hoja_resumen_ejecutivo(df_limpios, df_validados),
        "Producción por servicio" : hoja_produccion_servicios(df_limpios),
        "Top diagnósticos"        : hoja_top_diagnosticos(df_limpios),
        "Producción por IPS"      : hoja_produccion_ips(df_limpios),
        "Demografía"              : hoja_distribucion_demografica(df_limpios),
        "Evolución mensual"       : hoja_evolucion_mensual(df_limpios),
        "Registros con errores"   : hoja_registros_con_errores(df_validados)
    }

    with pd.ExcelWriter(RUTA_REPORTE, engine="openpyxl") as writer:
        for nombre_hoja, df_hoja in hojas.items():
            df_hoja.to_excel(writer, sheet_name=nombre_hoja, index=False)
            hoja = writer.sheets[nombre_hoja]
            for col in hoja.columns:
                max_ancho = max(
                    len(str(col[0].value)) if col[0].value else 0,
                    *[len(str(cell.value)) if cell.value else 0 for cell in col[1:]]
                )
                hoja.column_dimensions[col[0].column_letter].width = min(max_ancho + 4, 50)

    print(f"\nReporte ejecutivo generado en: {RUTA_REPORTE}")
    print(f"Hojas incluidas: {', '.join(hojas.keys())}")


# -----------------------------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# -----------------------------------------------------------------------------

def ejecutar_reporte():
    print("Generando reporte ejecutivo...")
    df_limpios, df_validados = cargar_datos()
    generar_reporte_excel(df_limpios, df_validados)
    print("Reporte generado exitosamente.")


if __name__ == "__main__":
    ejecutar_reporte()
