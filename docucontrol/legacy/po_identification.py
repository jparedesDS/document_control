import re
import pandas as pd


def identificar_cliente_por_PO(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "21472": "TECHNIP/SYNKEDIA",
        "10121": "DUQM",
        "10150": "BAPCO",
        "10160": "CRISP",
        "10230": "MARJAN",
        "10318": "RAS TANURA",
        "10330": "NEW PTA COMPLEX",
        "10370": "QATAR EPC3",
        "10380": "YPF",
        "10400": "ADNOC DALMA",
        "10430": "QATAR EPC4",
    }
    regex_pattern = r"^(\d{5})"
    df["Cliente"] = df["PO"].apply(lambda x: mapping.get(re.match(regex_pattern, str(x)).group(1), "") if re.match(regex_pattern, str(x)) else "")
    return df


def identificar_cliente_por_PO_PRODOC(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "21472": "TECHNIP/SYNKEDIA",
        "10121": "DUQM",
        "10150": "BAPCO",
        "10160": "CRISP",
        "10230": "MARJAN",
        "10318": "RAS TANURA",
        "10330": "NEW PTA COMPLEX",
        "10370": "QATAR EPC3",
        "10380": "YPF",
        "10400": "ADNOC DALMA",
        "10430": "QATAR EPC4",
    }
    regex_pattern = r"^(\d{5})"
    df["Cliente"] = df["P.O."].apply(lambda x: mapping.get(re.match(regex_pattern, str(x)).group(1), "") if re.match(regex_pattern, str(x)) else "")
    return df

