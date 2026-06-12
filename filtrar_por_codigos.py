import pandas as pd


def filtrar_por_codigos(
    codigos_path: str,
    codigos_col: str,
    datos_path: str,
    datos_col: str,
    output_path: str,
    codigos_tiene_encabezado: bool = False,
    datos_tiene_encabezado: bool = False,
):
    """
    Lee los códigos de codigos_path y extrae de datos_path todas las filas
    cuyo valor en datos_col coincida con algún código. Guarda el resultado en output_path.

    Los parámetros de columna aceptan nombre de encabezado o letra Excel ("A", "M", etc.).
    Usar codigos_tiene_encabezado=True / datos_tiene_encabezado=True si el archivo
    tiene fila de encabezado en la primera fila.
    """
    codigos_header = 0 if codigos_tiene_encabezado else None
    datos_header = 0 if datos_tiene_encabezado else None
    #SI ES UNA SOLA HOJA USAR ESTE
    #df_codigos = pd.read_excel(codigos_path, sheet_name=3, header=codigos_header)
    sheets = pd.read_excel(codigos_path, sheet_name=[1, 2], header=codigos_header)
    df_codigos = pd.concat(sheets.values(), ignore_index=True)
    df_datos = pd.read_excel(datos_path, header=datos_header)

    col_ref = _resolve_col(df_codigos, codigos_col)
    col_datos = _resolve_col(df_datos, datos_col)

    codigos = df_codigos[col_ref].dropna().unique()
    codigos_numeric = pd.to_numeric(pd.Series(codigos), errors="coerce").dropna()
    codigos_str = pd.Series(codigos).astype(str).str.strip()

    # Comparar como numérico si es posible, si no como string
    datos_key = pd.to_numeric(df_datos[col_datos], errors="coerce")
    #     # DEBUG — pegar antes de mask_numeric = ...
    # print("=== CÓDIGOS ===")
    # print(f"  tipo: {type(codigos[0])}, valor: {repr(codigos[0])}")
    # print(f"  codigos_numeric: {list(codigos_numeric[:3])}")
    # print(f" cantidad codigos mufas = {len(codigos_numeric)}")
    # print(f"  codigos_str: {list(codigos_str[:3])}")

    # print("=== DATOS col A ===")
    # muestra = df_datos[col_datos].dropna().head(3)
    # print(f"  tipo: {type(muestra.iloc[0])}, valor: {repr(muestra.iloc[0])}")
    # datos_key_muestra = pd.to_numeric(muestra, errors="coerce")
    # print(f"  como numérico: {list(datos_key_muestra)}")
    # print(f"  como string: {list(muestra.astype(str).str.strip())}")

    # print("=== INTERSECCIÓN ===")
    # print(f"  numérica: {set(datos_key_muestra.dropna()).intersection(set(codigos_numeric))}")
    # print(f"  string:   {set(muestra.astype(str).str.strip()).intersection(set(codigos_str[:10]))}")

#FIN DEBUG
    mask_numeric = datos_key.isin(codigos_numeric)
    mask_str = df_datos[col_datos].astype(str).str.strip().isin(codigos_str)

# DEBUG DIRECTO — agregar aquí
    print(f"mask_numeric hits: {mask_numeric.sum()}")
    print(f"mask_str hits: {mask_str.sum()}")
    # Busca el primer código directamente en la columna completa
    c0 = codigos_numeric.iloc[0]
    print(f"Buscando {c0} directamente en datos_key: {(datos_key == c0).any()}")
    print(f"datos_key sample completo (no null): {datos_key.dropna().unique()[:8]}")

    mask = mask_numeric | mask_str

    resultado = df_datos[mask].copy()
    resultado.to_excel(output_path, index=False)

    encontrados_numeric = datos_key[mask_numeric].dropna().unique()
    encontrados_str = df_datos[col_datos][mask_str].astype(str).str.strip().unique()
    no_encontrados = [
        c for c in codigos
        if str(c).strip() not in encontrados_str
        and not pd.to_numeric(pd.Series([c]), errors="coerce").isin(encontrados_numeric).any()
    ]

    print(f"{len(resultado)} filas encontradas de {len(df_datos)} totales.")
    if no_encontrados:
        print(f"\n{len(no_encontrados)} código(s) no encontrados:")
        for c in no_encontrados:
            print(f"  - {c}")
    else:
        print("Todos los códigos fueron encontrados.")
    print(f"\nArchivo guardado en: {output_path}")


def _resolve_col(df: pd.DataFrame, col: str) -> str:
    if col in df.columns:
        return col
    col_upper = col.upper()
    idx = 0
    for ch in col_upper:
        idx = idx * 26 + (ord(ch) - ord("A") + 1)
    idx -= 1
    if idx < 0 or idx >= len(df.columns):
        raise ValueError(f"Columna '{col}' fuera de rango. Columnas disponibles: {list(df.columns)}")
    return df.columns[idx]


if __name__ == "__main__":
    filtrar_por_codigos(
        codigos_path="data_xlsx/AVENIDA_ORIENTAL_PCS.xlsx",
        codigos_col="A",
        datos_path="data_xlsx/t10/10-term_empalme_excel.xlsx",
        datos_col="D",
        output_path="data_xlsx/target.xlsx",
    )
