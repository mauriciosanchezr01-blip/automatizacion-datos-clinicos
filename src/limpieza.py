# =============================================================================
# limpieza.py
# Proyecto: Automatización de Datos Clínicos
# Autor: Mauricio Sánchez
# Descripción: Limpieza y estandarización de registros clínicos
# =============================================================================

import pandas as pd
import numpy as np
import os
import re

# -----------------------------------------------------------------------------
# CONFIGURACIÓN
# -----------------------------------------------------------------------------

RUTA_ENTRADA = "data/processed/registros_validados.csv"
RUTA_SALIDA  = "data/processed/registros_limpios.csv"


# -----------------------------------------------------------------------------
# CARGA DE DATOS
# -----------------------------------------------------------------------------

def cargar_datos(ruta: str) -> pd.DataFrame:
    """Carga el archivo de registros validados."""
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
    df = pd.read_csv(ruta, dtype=str, encoding="utf-8")
    print(f"Registros cargados para limpieza: {len(df)}")
    return df


# -----------------------------------------------------------------------------
# FUNCIONES DE LIMPIEZA
# -----------------------------------------------------------------------------

def estandarizar_texto(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina espacios, convierte a mayúsculas los campos de texto clave."""
    columnas_texto = [
        "tipo_documento", "sexo", "descripcion_servicio",
        "descripcion_diagnostico", "municipio", "departamento"
    ]
    for col in columnas_texto:
        if col in df.columns:
            df[col] = df[col].str.strip().str.upper()
    return df


def limpiar_numeros_documento(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina caracteres no numéricos del número de documento."""
    df["numero_documento"] = df["numero_documento"].apply(
        lambda x: re.sub(r"\D", "", str(x)) if pd.notnull(x) else x
    )
    return df


def convertir_fechas(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte columnas de fecha al formato estándar datetime."""
    for col in ["fecha_atencion", "fecha_nacimiento"]:
        df[col] = pd.to_datetime(df[col], errors="coerce", format="%Y-%m-%d")
    return df


def calcular_edad(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula la edad del paciente en años al momento de la atención."""
    df["edad_años"] = (
        (df["fecha_atencion"] - df["fecha_nacimiento"]).dt.days / 365.25
    ).apply(lambda x: int(x) if pd.notnull(x) and x >= 0 else np.nan)
    return df


def clasificar_grupo_etario(df: pd.DataFrame) -> pd.DataFrame:
    """Clasifica al paciente en grupo etario según estándares del MSPS."""
    def grupo(edad):
        if pd.isnull(edad):
            return "Sin dato"
        elif edad < 1:
            return "Menor de 1 año"
        elif edad < 5:
            return "1 a 4 años"
        elif edad < 15:
            return "5 a 14 años"
        elif edad < 30:
            return "15 a 29 años"
        elif edad < 45:
            return "30 a 44 años"
        elif edad < 60:
            return "45 a 59 años"
        else:
            return "60 años y más"

    df["grupo_etario"] = df["edad_años"].apply(grupo)
    return df


def convertir_valor_servicio(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte el valor del servicio a tipo numérico."""
    df["valor_servicio"] = pd.to_numeric(df["valor_servicio"], errors="coerce")
    return df


def estandarizar_codigo_diagnostico(df: pd.DataFrame) -> pd.DataFrame:
    """Estandariza el código CIE-10 eliminando espacios y en mayúsculas."""
    df["codigo_diagnostico"] = (
        df["codigo_diagnostico"]
        .str.strip()
        .str.upper()
        .str.replace(" ", "", regex=False)
    )
    return df


def eliminar_registros_rechazados(df: pd.DataFrame) -> pd.DataFrame:
    """Filtra l
