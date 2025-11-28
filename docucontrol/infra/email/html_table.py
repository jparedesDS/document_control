from __future__ import annotations

import pandas as pd


def dataframe_to_highlighted_html(df: pd.DataFrame) -> str:
    df = df.fillna("")

    def highlight(val: str) -> str:
        return f'<span style="background-color: yellow">{val}</span>'

    styled = df.copy()
    if "Return Days" in styled.columns:
        styled["Return Days"] = styled["Return Days"].apply(
            lambda v: highlight(f'<b><span style="color:red">{v}</span></b>')
        )
    if "Doc. Sent Date" in styled.columns:
        styled["Doc. Sent Date"] = styled["Doc. Sent Date"].apply(highlight)

    header_style = [
        {
            "selector": "th",
            "props": [
                ("background-color", "#6678AF"),
                ("color", "#FFFFFF"),
                ("text-align", "center"),
                ("font-size", "14px"),
                ("font-weight", "bold"),
            ],
        }
    ]

    table = styled.style.set_table_styles(header_style)
    cell_style = "background-color: #D4DCF4; color: #000000; text-align: left; font-size: 14px;"
    for col in styled.columns:
        table = table.map(lambda _: cell_style, subset=[col])

    estado_col = None
    if "Status" in styled.columns:
        estado_col = "Status"
    elif "Estado" in styled.columns:
        estado_col = "Estado"

    if estado_col:
        estado_colors = {
            "Rechazado": "background-color:#F8B4B4; color:#000;",
            "Comentado": "background-color:#FFE599; color:#000;",
            "Aprobado": "background-color:#00D25F; color:#000;",
            "Submitted": "background-color:#B1E1B9; color:#000;",
        }

        def estado_style(val: str) -> str:
            val_lower = str(val).lower()
            for key, css in estado_colors.items():
                if key.lower() in val_lower:
                    return css
            return "background-color:#D4DCF4; color:#000;"

        table = table.map(estado_style, subset=[estado_col])

    table = table.hide(axis="index")
    return table.to_html(escape=False)

