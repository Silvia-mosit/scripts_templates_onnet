import pandas as pd
import openpyxl
from openpyxl.utils import column_index_from_string


def buscar_y_escribir(
    codigos_path: str,
    codigos_col: str,
    datos_path: str,
    buscar_col: str,
    escribir_col: str,
    primera_fila_datos: int = 5,
):
    """
    Lee códigos de codigos_path (columna codigos_col, sin encabezado) y para cada fila
    de datos_path donde buscar_col coincide con un código, escribe ese código en
    escribir_col. Preserva todo el formato de datos_path.

    primera_fila_datos: fila Excel 1-based donde empiezan los datos (por defecto 5).
    Columnas se expresan como letras Excel ("H", "BV", etc.).
    """
    # Leer códigos (archivo sin encabezado)
    df_codigos = pd.read_excel(codigos_path, header=None)
    col_idx = _letra_a_idx0(codigos_col)
    codigos_raw = df_codigos.iloc[:, col_idx].dropna()

    # Índices numérico y string para comparación flexible
    codigos_num = set()
    codigos_str = set()
    for c in codigos_raw:
        try:
            codigos_num.add(int(c))
        except (ValueError, TypeError):
            pass
        codigos_str.add(str(c).strip())

    # Abrir con openpyxl para preservar formato
    wb = openpyxl.load_workbook(datos_path)
    ws = wb.active

    col_buscar = column_index_from_string(buscar_col.upper())    # 1-based
    col_escribir = column_index_from_string(escribir_col.upper())  # 1-based

    encontrados = 0
    for row in ws.iter_rows(min_row=primera_fila_datos):
        cell_val = row[col_buscar - 1].value
        if cell_val is None:
            continue

        matched = False
        try:
            if int(cell_val) in codigos_num:
                matched = True
        except (ValueError, TypeError):
            pass
        if not matched and str(cell_val).strip() in codigos_str:
            matched = True

        if matched:
            row[col_escribir - 1].value = cell_val
            encontrados += 1

    wb.save(datos_path)
    print(f"{encontrados} fila(s) encontradas y escritas en columna {escribir_col}.")
    print(f"Archivo guardado: {datos_path}")


def _letra_a_idx0(col: str) -> int:
    """Convierte letra Excel ('A', 'F', 'BV'...) a índice 0-based."""
    idx = 0
    for ch in col.upper():
        idx = idx * 26 + (ord(ch) - ord("A") + 1)
    return idx - 1


if __name__ == "__main__":
    buscar_y_escribir(
        codigos_path="data_xlsx/14_conn_por_col_v3_actual_copy.xlsx",
        codigos_col="F",
        datos_path="data_xlsx/nva_sanantonio_processed_v3.xlsx",
        buscar_col="H",
        escribir_col="BV",
        primera_fila_datos=5,
    )
