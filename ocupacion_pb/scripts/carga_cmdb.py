import pandas as pd
from pathlib import Path

CARGA_PATH    = "../data_general/Carga_CMDB_Ocupacion_OLT-VALDIVIA.csv"
BUSQUEDA_PATH = "../data_general/VALDIVIA_copy.csv"
OLT_PATH      = "../data_general/Consolidado_OLT.xlsx"
T11_PARES_PATH = "../data_general/T11_Tramo_VALDIVIA_cta_pares.csv"

# Nombres de columna por posicion (evita hardcodear si cambian)
COL_BUSQUEDA_KEY = "CODIGO EQUIPO"      # col U (idx 20) en BUSQUEDA_PATH
COL_BUSQUEDA_CAP = "CAP"               # col E (idx  4) en BUSQUEDA_PATH
COL_T11_KEY      = "logicalCableId.NUM" # col E (idx  4) en T11_PARES_PATH
COL_T11_RESULT   = "ParentRefNum"       # col A (idx  0) en T11_PARES_PATH
COL_CARGA_KEY    = "TERM_EQPT_CODE"    # col H (idx  7) en CARGA_PATH
COL_CARGA_OUT    = "SP_CABLE_NUM_IN"   # col I (idx  8) en CARGA_PATH — columna de salida


def _output_path(path: str) -> str:
    p = Path(path)
    return str(p.with_stem(p.stem + "_output"))


def cargar_archivos() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df_carga    = pd.read_csv(CARGA_PATH,    sep="|", encoding="latin-1")
    df_busqueda = pd.read_csv(BUSQUEDA_PATH, sep=";", encoding="latin-1")

    df_t11 = pd.read_csv(
        T11_PARES_PATH, sep=";", encoding="latin-1",
        skiprows=[0, 2, 3], header=0
      )
    # df_t11 = pd.read_csv(
    #     T11_PARES_PATH, sep=None, engine="python", encoding="latin-1",
    #     skiprows=[0, 2, 3], header=0
    # )
    print("Columnas df_carga:", df_carga.columns.tolist())
    print("Columnas df_busqueda:", df_busqueda.columns.tolist())
    return df_carga, df_busqueda, df_t11


def obtener_cap_por_codigo(df_carga: pd.DataFrame, df_busqueda: pd.DataFrame) -> list:
    """Busca cada TERM_EQPT_CODE en col U de BUSQUEDA y devuelve los valores de col E (CAP)."""
    codigos = set(df_carga["TERM_EQPT_CODE"].dropna().unique())
    filas   = df_busqueda[df_busqueda[COL_BUSQUEDA_KEY].isin(codigos)]
    caps    = filas[COL_BUSQUEDA_CAP].dropna().unique().tolist()
    return caps


def obtener_parent_ref_por_cap(caps: list, df_t11: pd.DataFrame) -> list:
    """Busca cada CAP en col E de T11 y devuelve los valores de col A (ParentRefNum)."""
    filas = df_t11[df_t11[COL_T11_KEY].isin(caps)]
    return filas[COL_T11_RESULT].dropna().tolist()


def agregar_parent_ref_en_carga(
    df_carga: pd.DataFrame, df_busqueda: pd.DataFrame, df_t11: pd.DataFrame
) -> pd.DataFrame:
    """Escribe en col I (SP_CABLE_NUM_IN) el ParentRefNum correspondiente a cada fila."""
    mapa_codigo_cap = (
        df_busqueda.dropna(subset=[COL_BUSQUEDA_KEY, COL_BUSQUEDA_CAP])
        .drop_duplicates(subset=[COL_BUSQUEDA_KEY])
        .set_index(COL_BUSQUEDA_KEY)[COL_BUSQUEDA_CAP]
    )
    mapa_cap_parent = (
        df_t11.dropna(subset=[COL_T11_KEY, COL_T11_RESULT])
        .drop_duplicates(subset=[COL_T11_KEY])
        .set_index(COL_T11_KEY)[COL_T11_RESULT]
    )
    df_out = df_carga.copy()
    df_out[COL_CARGA_OUT] = (
        df_out[COL_CARGA_KEY].map(mapa_codigo_cap).map(mapa_cap_parent).astype("Int64")
    )
    return df_out


def generar_salida(df: pd.DataFrame, carga_path: str = CARGA_PATH) -> None:
    """Guarda copia de CARGA_PATH con col I actualizada."""
    out = _output_path(carga_path)
    df.to_csv(out, sep=",", index=False)
    print(f"Archivo generado: {out}")


if __name__ == "__main__":
    df_carga, df_busqueda, df_t11 = cargar_archivos()

    caps        = obtener_cap_por_codigo(df_carga, df_busqueda)
    parent_refs = obtener_parent_ref_por_cap(caps, df_t11)
    print(f"CAPs encontrados ({len(caps)}): {caps[:10]}")
    print(f"ParentRefNums encontrados ({len(parent_refs)}): {parent_refs[:10]}")

    df_resultado = agregar_parent_ref_en_carga(df_carga, df_busqueda, df_t11)
    print(f"\n=== Primeras 10 filas — col I actualizada ===")
    print(df_resultado[[COL_CARGA_KEY, COL_CARGA_OUT]].head(10).to_string())

    generar_salida(df_resultado)



