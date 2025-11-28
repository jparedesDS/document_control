import numpy as np
import pandas as pd


def prodoc_vendor_number(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "7011318362": "P-24/091",
        "7070000087": "P-24/054",
        "7011319592": "P-24/073",
        "7011294464": "P-23/087",
        "600017293": "P-23/097",
        "7011265051": "P-24/006",
        "7080111164": "P-24/023",
        "7080113517": "P-24/044",
        "7011295889": "P-24/050",
        "7080115423": "P-24/058",
        "7080115700": "P-24/060",
    }
    df["Nº Pedido"] = df["Nº Pedido"].astype(str).str.strip()
    df["Nº Pedido"] = df["Nº Pedido"].map(mapping).fillna(df["Nº Pedido"])
    return df


def reconocer_tipo_proyecto(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "7011318362": "CAUDAL",
        "7070000087": "TEMPERATURA",
        "7011319592": "TEMPERATURA",
        "7011294464": "PLACAS",
        "600017293": "P-23/097",
        "7011265051": "P-24/006",
        "7080111164": "P-24/023",
        "7080113517": "P-24/044",
        "7011295889": "P-24/050",
        "7080115423": "P-24/058",
        "7080115700": "P-24/060",
    }
    df["Material"] = df["PO"].map(mapping).fillna(df["PO"])
    return df


def procesar_documento_y_fecha(df: pd.DataFrame, receivedtime):
    mapping = {
        "PLG": "Planos",
        "DWG": "Planos",
        "CAL": "Cálculos",
        "ESP": "Cálculos y Planos",
        "CER": "Certificado",
        "NACE": "Certificado",
        "DOS": "Dossier",
        "LIS": "Listado",
        "ITP": "Procedimientos",
        "PRC": "Procedimientos",
        "MAN": "Manual",
        "VDB": "Listado",
        "PLN": "PPI",
        "PLD": "Nameplate",
        "CAT": "Catalogo",
        "DL": "Listado",
        "SPL": "Repuestos",
    }
    df["Tipo de documento"] = df["Tipo de documento"].map(mapping)
    df["Fecha"] = pd.to_datetime(receivedtime, dayfirst=True)
    return df


def critico(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "Planos": "Sí",
        "Cálculos": "Sí",
        "Cálculos y Planos": "Sí",
        "Certificado": "No",
        "Dossier": "No",
        "Procedimientos": "No",
        "Manual": "Sí",
        "PPI": "Sí",
        "Nameplate": "No",
        "Catalogo": "Sí",
        "Listado": "Sí",
        "Repuestos": "No",
    }
    df["Crítico"] = df["Tipo de documento"].map(mapping)
    return df


def cambiar_tipo_estado(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "A - REJECTED": "Rechazado",
        "1 - WITH COMMENTS": "Com. Mayores",
        "2 - WITHOUT COMMENTS": "Aprobado",
        "2I - FOR INFORMATION ONLY": "Informativo",
        "3 - WITH MINOR COMMENTS": "Com. Menores",
    }
    df["S.R. Status"] = df["S.R. Status"].map(mapping)
    return df


def reemplazar_null(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {np.nan: "S00", "S01": "S01", "S02": "S02", "S03": "S03", "S04": "S04", "S05": "S05", "S06": "S06", "S07": "S07"}
    df["Supp."] = df["Supp."].map(mapping).fillna("S00")
    return df

