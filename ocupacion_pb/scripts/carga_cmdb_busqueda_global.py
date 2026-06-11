import pandas as pd
from pathlib import Path

CARGA_PATH    = "../data_general/Carga_CMDB_Ocupacion_OLT-PENCO_COPY.csv"
EXCEL_PATH    = "../data_general/busqueda_global.xlsx"   # Excel con 2+ hojas de valores a buscar

COL_MATCH_VALUE = "MATCH_VALUE"   # valor encontrado
COL_MATCH_SHEET = "MATCH_SHEET"   # hoja del Excel donde estaba el valor
COL_MATCH_COL   = "MATCH_COL"     # columna de CARGA donde se encontró


def _output_path(path: str) -> str:
    p = Path(path)
    return str(p.with_stem(p.stem + "_output"))


def cargar_archivos() -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    df_carga = pd.read_csv(CARGA_PATH, sep="|", encoding="latin-1", dtype=str)

    hojas: dict[str, pd.DataFrame] = pd.read_excel(EXCEL_PATH, sheet_name=None, dtype=str)

    print("Columnas df_carga:", df_carga.columns.tolist())
    print("Hojas Excel:", list(hojas.keys()))
    return df_carga, hojas


def recopilar_valores(hojas: dict[str, pd.DataFrame]) -> dict[str, str]:
    """Devuelve {valor: nombre_hoja} con todos los valores únicos de todas las hojas."""
    valores: dict[str, str] = {}
    for nombre_hoja, df in hojas.items():
        for val in df.values.flatten():
            if pd.notna(val) and str(val).strip():
                valores[str(val).strip()] = nombre_hoja
    print(f"Total valores a buscar: {len(valores)}")
    return valores


def buscar_en_carga(
    df_carga: pd.DataFrame, valores: dict[str, str]
) -> pd.DataFrame:
    """
    Busca cada valor en cualquier celda de df_carga.
    Devuelve df_carga con columnas extra: MATCH_VALUE, MATCH_SHEET, MATCH_COL.
    Una fila puede aparecer varias veces si coincide con más de un valor.
    """
    df_str = df_carga.astype(str)

    resultados = []
    for valor, hoja in valores.items():
        mask = df_str.apply(lambda col: col.str.strip() == valor).any(axis=1)
        if not mask.any():
            continue
        filas = df_carga[mask].copy()
        # columna donde se encontró (primera coincidencia por fila)
        filas[COL_MATCH_COL] = df_str[mask].apply(
            lambda row: next(
                (c for c in df_str.columns if row[c].strip() == valor), ""
            ),
            axis=1,
        )
        filas[COL_MATCH_VALUE] = valor
        filas[COL_MATCH_SHEET] = hoja
        resultados.append(filas)

    if not resultados:
        print("No se encontraron coincidencias.")
        return pd.DataFrame(columns=list(df_carga.columns) + [COL_MATCH_VALUE, COL_MATCH_SHEET, COL_MATCH_COL])

    df_out = pd.concat(resultados, ignore_index=True)
    print(f"Filas con coincidencia: {len(df_out)}")
    return df_out


def generar_salida(df: pd.DataFrame, carga_path: str = CARGA_PATH) -> None:
    out = _output_path(carga_path)
    df.to_csv(out, sep=",", index=False)
    print(f"Archivo generado: {out}")


if __name__ == "__main__":
    df_carga, hojas = cargar_archivos()

    valores = recopilar_valores(hojas)
    df_resultado = buscar_en_carga(df_carga, valores)

    print(f"\n=== Primeras 10 coincidencias ===")
    cols_vista = [COL_MATCH_SHEET, COL_MATCH_COL, COL_MATCH_VALUE]
    print(df_resultado[cols_vista].head(10).to_string())

    generar_salida(df_resultado)
