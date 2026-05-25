# =============================================================================
# validacion.py
# Proyecto: Automatización de Datos Clínicos
# Autor: Mauricio Sánchez
# Descripción: Validación de registros clínicos según normativa colombiana
# =============================================================================

import pandas as pd
import numpy as np
from datetime import datetime
import os

# -----------------------------------------------------------------------------
# CONFIGURACIÓN
# -----------------------------------------------------------------------------

RUTA_ENTRADA = "data/raw/registros_clinicos.csv"
RUTA_SALIDA  = "data/processed/registros_validados.csv"

TIPOS_DOCUMENTO_VALIDOS = ["CC", "TI", "CE", "PA", "RC", "MS", "AS"]
SEXOS_VALIDOS           = ["M", "F"]
CODIGOS_SERVICIO_VALIDOS = ["890301", "890401", "890601", "890701", "890801"]
FECHA_MINIMA            = datetime(2000, 1, 1)
FECHA_MAXIMA            = datetime.today()


# -----------------------------------------------------------------------------
# CARGA DE DATOS
# -----------------------------------------------------------------------------

def cargar_datos(ruta: str) -> pd.DataFrame:
    """Carga el archivo de registros clínicos."""
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
    df = pd.read_csv(ruta, dtype=str, encoding="utf-8")
    print(f"Registros cargados: {len(df)}")
    return df


# -----------------------------------------------------------------------------
# REGLAS DE VALIDACIÓN
# -----------------------------------------------------------------------------

def validar_campos_obligatorios(df: pd.DataFrame) -> pd.DataFrame:
    """Detecta registros con campos obligatorios vacíos."""
    campos = [
        "id_paciente", "tipo_documento", "numero_documento",
        "fecha_nacimiento", "sexo", "codigo_servicio",
        "codigo_diagnostico", "fecha_atencion", "valor_servicio"
    ]
    for campo in campos:
        df[f"error_{campo}_vacio"] = df[campo].isnull() | (df[campo].str.strip() == "")
    return df


def validar_tipo_documento(df: pd.DataFrame) -> pd.DataFrame:
    """Valida que el tipo de documento sea uno de los permitidos."""
    df["error_tipo_documento"] = ~df["tipo_documento"].isin(TIPOS_DOCUMENTO_VALIDOS)
    return df


def validar_sexo(df: pd.DataFrame) -> pd.DataFrame:
    """Valida que el sexo sea M o F."""
    df["error_sexo"] = ~df["sexo"].isin(SEXOS_VALIDOS)
    return df


def validar_fechas(df: pd.DataFrame) -> pd.DataFrame:
    """Valida formato y coherencia de fechas."""
    def es_fecha_valida(valor):
        try:
            fecha = datetime.strptime(str(valor), "%Y-%m-%d")
            return FECHA_MINIMA <= fecha <= FECHA_MAXIMA
        except Exception:
            return False

    df["error_fecha_atencion"]    = ~df["fecha_atencion"].apply(es_fecha_valida)
    df["error_fecha_nacimiento"]  = ~df["fecha_nacimiento"].apply(es_fecha_valida)
    return df


def validar_valor_servicio(df: pd.DataFrame) -> pd.DataFrame:
    """Valida que el valor del servicio sea un número positivo."""
    def es_valor_valido(valor):
        try:
            return float(valor) > 0
        except Exception:
            return False

    df["error_valor_negativo"] = ~df["valor_servicio"].apply(es_valor_valido)
    return df


def detectar_duplicados(df: pd.DataFrame) -> pd.DataFrame:
    """Detecta registros duplicados por paciente, fecha y servicio."""
    columnas_clave = ["id_paciente", "fecha_atencion", "codigo_servicio"]
    df["error_duplicado"] = df.duplicated(subset=columnas_clave, keep=False)
    return df


def validar_codigo_diagnostico(df: pd.DataFrame) -> pd.DataFrame:
    """Valida que el código diagnóstico no esté vacío."""
    df["error_diagnostico_vacio"] = (
        df["codigo_diagnostico"].isnull() |
        (df["codigo_diagnostico"].str.strip() == "")
    )
    return df


# -----------------------------------------------------------------------------
# CONSOLIDACIÓN DE ERRORES
# -----------------------------------------------------------------------------

def consolidar_errores(df: pd.DataFrame) -> pd.DataFrame:
    """Cuenta el total de errores por registro y clasifica su estado."""
    columnas_error = [c for c in df.columns if c.startswith("error_")]
    df[columnas_error] = df[columnas_error].fillna(False)
    df["total_errores"] = df[columnas_error].sum(axis=1)
    df["estado_registro"] = df["total_errores"].apply(
        lambda x: "VÁLIDO" if x == 0 else ("ADVERTENCIA" if x == 1 else "RECHAZADO")
    )
    return df


# -----------------------------------------------------------------------------
# RESUMEN EJECUTIVO
# -----------------------------------------------------------------------------

def generar_resumen(df: pd.DataFrame) -> None:
    """Imprime un resumen ejecutivo de la validación."""
    total         = len(df)
    validos       = (df["estado_registro"] == "VÁLIDO").sum()
    advertencias  = (df["estado_registro"] == "ADVERTENCIA").sum()
    rechazados    = (df["estado_registro"] == "RECHAZADO").sum()

    print("\n" + "=" * 55)
    print("   RESUMEN DE VALIDACIÓN — REGISTROS CLÍNICOS")
    print("=" * 55)
    print(f"  Total de registros procesados : {total}")
    print(f"  Registros válidos             : {validos}  ({validos/total*100:.1f}%)")
    print(f"  Registros con advertencia     : {advertencias}  ({advertencias/total*100:.1f}%)")
    print(f"  Registros rechazados          : {rechazados}  ({rechazados/total*100:.1f}%)")
    print("=" * 55)

    columnas_error = [c for c in df.columns if c.startswith("error_")]
    print("\n  Errores detectados por tipo:")
    for col in columnas_error:
        cantidad = df[col].sum()
        if cantidad > 0:
            nombre = col.replace("error_", "").replace("_", " ").capitalize()
            print(f"  - {nombre:<35} {int(cantidad)} registro(s)")
    print("=" * 55 + "\n")


# -----------------------------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# -----------------------------------------------------------------------------

def ejecutar_pipeline():
    print("Iniciando validación de registros clínicos...")

    df = cargar_datos(RUTA_ENTRADA)

    df = validar_campos_obligatorios(df)
    df = validar_tipo_documento(df)
    df = validar_sexo(df)
    df = validar_fechas(df)
    df = validar_valor_servicio(df)
    df = detectar_duplicados(df)
    df = validar_codigo_diagnostico(df)
    df = consolidar_errores(df)

    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(RUTA_SALIDA, index=False, encoding="utf-8")

    generar_resumen(df)
    print(f"Archivo procesado guardado en: {RUTA_SALIDA}")


if __name__ == "__main__":
    ejecutar_pipeline()
