# =============================================================================
# indicadores.py
# Proyecto: Automatización de Datos Clínicos
# Autor: Mauricio Sánchez
# Descripción: Cálculo de indicadores clave de calidad del dato y operativos
# =============================================================================

import pandas as pd
import numpy as np
import os

# -----------------------------------------------------------------------------
# CONFIGURACIÓN
# -----------------------------------------------------------------------------

RUTA_ENTRADA = "data/processed/registros_limpios.csv"
RUTA_SALIDA  = "data/processed/indicadores_resumen.csv"


# -----------------------------------------------------------------------------
# CARGA DE DATOS
# -----------------------------------------------------------------------------

def cargar_datos(ruta: str) -> pd.DataFrame:
    """Carga el archivo de registros limpios."""
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
    df = pd.read_csv(ruta, encoding="utf-8")
    df["fecha_atencion"]   = pd.to_datetime(df["fecha_atencion"],   errors="coerce")
    df["fecha_nacimiento"] = pd.to_datetime(df["fecha_nacimiento"], errors="coerce")
    df["valor_servicio"]   = pd.to_numeric(df["valor_servicio"],    errors="coerce")
    print(f"Registros cargados para indicadores: {len(df)}")
    return df


# -----------------------------------------------------------------------------
# INDICADORES DE CALIDAD DEL DATO
# -----------------------------------------------------------------------------

def indicador_completitud(df: pd.DataFrame) -> dict:
    """Calcula el porcentaje de completitud por campo obligatorio."""
    campos = [
        "id_paciente", "tipo_documento", "numero_documento",
        "fecha_nacimiento", "sexo", "codigo_servicio",
        "codigo_diagnostico", "fecha_atencion", "valor_servicio",
        "codigo_medico", "codigo_ips"
    ]
    total = len(df)
    resultado = {}
    for campo in campos:
        if campo in df.columns:
            completos = df[campo].notnull().sum()
            resultado[campo] = round((completos / total) * 100, 2)
    return resultado


def indicador_tasa_error(df: pd.DataFrame) -> dict:
    """Calcula la tasa de error global y por tipo."""
    columnas_error = [c for c in df.columns if c.startswith("error_")]
    total = len(df)
    resultado = {}
    for col in columnas_error:
        if col in df.columns:
            cantidad = pd.to_numeric(df[col], errors="coerce").fillna(0).sum()
            nombre   = col.replace("error_", "").replace("_", " ").capitalize()
            resultado[nombre] = round((cantidad / total) * 100, 2)
    return resultado


def indicador_duplicados(df: pd.DataFrame) -> dict:
    """Calcula el porcentaje de registros duplicados."""
    total      = len(df)
    duplicados = df.duplicated(
        subset=["id_paciente", "fecha_atencion", "codigo_servicio"],
        keep=False
    ).sum()
    return {
        "total_duplicados"    : int(duplicados),
        "porcentaje_duplicados": round((duplicados / total) * 100, 2)
    }


# -----------------------------------------------------------------------------
# INDICADORES OPERATIVOS
# -----------------------------------------------------------------------------

def indicador_produccion_por_servicio(df: pd.DataFrame) -> pd.DataFrame:
    """Número de atenciones y valor total por tipo de servicio."""
    return (
        df.groupby("descripcion_servicio")
        .agg(
            total_atenciones=("id_registro", "count"),
            valor_total     =("valor_servicio", "sum"),
            valor_promedio  =("valor_servicio", "mean")
        )
        .round(2)
        .reset_index()
        .sort_values("total_atenciones", ascending=False)
    )


def indicador_produccion_por_ips(df: pd.DataFrame) -> pd.DataFrame:
    """Número de atenciones y valor facturado por IPS."""
    return (
        df.groupby(["codigo_ips", "municipio"])
        .agg(
            total_atenciones=("id_registro", "count"),
            valor_total     =("valor_servicio", "sum"),
            pacientes_unicos=("id_paciente", "nunique")
        )
        .round(2)
        .reset_index()
        .sort_values("total_atenciones", ascending=False)
    )


def indicador_top_diagnosticos(df: pd.DataFrame, top: int = 10) -> pd.DataFrame:
    """Top diagnósticos más frecuentes por código CIE-10."""
    return (
        df.groupby(["codigo_diagnostico", "descripcion_diagnostico"])
        .agg(frecuencia=("id_registro", "count"))
        .reset_index()
        .sort_values("frecuencia", ascending=False)
        .head(top)
    )


def indicador_distribucion_sexo(df: pd.DataFrame) -> pd.DataFrame:
    """Distribución de atenciones por sexo."""
    total = len(df)
    return (
        df.groupby("sexo")
        .agg(total_atenciones=("id_registro", "count"))
        .assign(porcentaje=lambda x: (x["total_atenciones"] / total * 100).round(2))
        .reset_index()
    )


def indicador_distribucion_etaria(df: pd.DataFrame) -> pd.DataFrame:
    """Distribución de atenciones por grupo etario."""
    total = len(df)
    orden = [
        "Menor de 1 año", "1 a 4 años", "5 a 14 años",
        "15 a 29 años", "30 a 44 años", "45 a 59 años",
        "60 años y más", "Sin dato"
    ]
    df["grupo_etario"] = pd.Categorical(
        df["grupo_etario"], categories=orden, ordered=True
    )
    return (
        df.groupby("grupo_etario", observed=True)
        .agg(total_atenciones=("id_registro", "count"))
        .assign(porcentaje=lambda x: (x["total_atenciones"] / total * 100).round(2))
        .reset_index()
    )


def indicador_produccion_mensual(df: pd.DataFrame) -> pd.DataFrame:
    """Evolución mensual de atenciones y valor facturado."""
    return (
        df.groupby("periodo")
        .agg(
            total_atenciones=("id_registro", "count"),
            valor_total     =("valor_servicio", "sum"),
            pacientes_unicos=("id_paciente", "nunique")
        )
        .round(2)
        .reset_index()
        .sort_values("periodo")
    )


# -----------------------------------------------------------------------------
# EXPORTAR RESUMEN CONSOLIDADO
# -----------------------------------------------------------------------------

def exportar_resumen(resultados: dict, ruta: str) -> None:
    """Exporta un resumen consolidado de indicadores a CSV."""
    filas = []
    for indicador, valor in resultados.items():
        if isinstance(valor, dict):
            for k, v in valor.items():
                filas.append({"indicador": indicador, "variable": k, "valor": v})
        else:
            filas.append({"indicador": indicador, "variable": "-", "valor": valor})

    pd.DataFrame(filas).to_csv(ruta, index=False, encoding="utf-8")
    print(f"Resumen de indicadores exportado en: {ruta}")


# -----------------------------------------------------------------------------
# RESUMEN EN CONSOLA
# -----------------------------------------------------------------------------

def imprimir_resumen(df: pd.DataFrame) -> None:
    """Imprime resumen ejecutivo de indicadores en consola."""
    print("\n" + "=" * 55)
    print("   INDICADORES OPERATIVOS — REGISTROS CLÍNICOS")
    print("=" * 55)
    print(f"\n  Total atenciones          : {len(df)}")
    print(f"  Pacientes únicos          : {df['id_paciente'].nunique()}")
    print(f"  IPS activas               : {df['codigo_ips'].nunique()}")
    print(f"  Valor total facturado      : $ {df['valor_servicio'].sum():,.0f}")
    print(f"  Valor promedio por atención: $ {df['valor_servicio'].mean():,.0f}")

    print("\n  Top 5 diagnósticos:")
    top = indicador_top_diagnosticos(df, top=5)
    for _, fila in top.iterrows():
        print(f"  - {fila['codigo_diagnostico']:<10} {fila['descripcion_diagnostico'][:35]:<35} {fila['frecuencia']} casos")

    print("\n  Producción por servicio:")
    prod = indicador_produccion_por_servicio(df)
    for _, fila in prod.iterrows():
        print(f"  - {fila['descripcion_servicio'][:40]:<40} {int(fila['total_atenciones'])} atenciones")

    print("=" * 55 + "\n")


# -----------------------------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# -----------------------------------------------------------------------------

def ejecutar_indicadores():
    print("Calculando indicadores de registros clínicos...")

    df = cargar_datos(RUTA_ENTRADA)

    resultados = {
        "completitud"  : indicador_completitud(df),
        "tasa_error"   : indicador_tasa_error(df),
        "duplicados"   : indicador_duplicados(df)
    }

    os.makedirs("data/processed", exist_ok=True)
    exportar_resumen(resultados, RUTA_SALIDA)
    imprimir_resumen(df)

    print("Indicadores calculados exitosamente.")


if __name__ == "__main__":
    ejecutar_indicadores()
