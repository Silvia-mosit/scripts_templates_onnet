import pandas as pd
from pathlib import Path

INPUT_FILE = Path("data_xlsx/t14/t14_DGO_inicial_general_ultimo.xlsx")
OUTPUT_FILE = Path("data_xlsx/target.xlsx")
COLUMN = "F"  # columna F (índice 5)


def buscar_por_zona(zona: str, input_file: Path = INPUT_FILE, output_file: Path = OUTPUT_FILE) -> pd.DataFrame:
    df = pd.read_excel(input_file, header=0)

    col_index = ord(COLUMN.upper()) - ord("A")
    col_name = df.columns[col_index]

    resultado = df[df[col_name].astype(str).str.strip().str.upper() == zona.strip().upper()]

    resultado.to_excel(output_file, index=False)
    print(f"Filas encontradas: {len(resultado)}")
    print(f"Guardado en: {output_file}")
    return resultado


if __name__ == "__main__":
    buscar_por_zona("AVENIDA ORIENTAL NTE PCS")
