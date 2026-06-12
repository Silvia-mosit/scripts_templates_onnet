import csv
import sys
import pandas as pd
from pathlib import Path


def _output_path(base: Path, suffix: str) -> Path:
    return base.with_stem(base.stem + suffix)


def _detectar_separador(archivo: str) -> str:
    with open(archivo, newline="", encoding="utf-8-sig") as f:
        muestra = f.read(4096)
    return csv.Sniffer().sniff(muestra).delimiter


def rechazar_eliminar(
    archivo: str,
    campo: str,
    valores: list[str],
    separador: str = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    p = Path(archivo)

    if p.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(archivo)
        separador = ";"
    else:
        if separador is None:
            separador = _detectar_separador(archivo)
        df = pd.read_csv(archivo, sep=separador, engine="python")

    if campo not in df.columns:
        raise ValueError(f"Campo '{campo}' no encontrado. Columnas disponibles: {list(df.columns)}")

    mascara = df[campo].astype(str).isin([str(v) for v in valores])
    df_rechazados = df[mascara].copy()
    df_limpio = df[~mascara].copy()

    out_limpio = _output_path(p, "_sin_rechazados")
    out_rechazados = _output_path(p, "_rechazados")

    df_limpio.to_csv(out_limpio.with_suffix(".csv"), sep=separador, index=False)
    df_rechazados.to_csv(out_rechazados.with_suffix(".csv"), sep=separador, index=False)

    print(f"Total registros originales : {len(df)}")
    print(f"Registros eliminados       : {len(df_rechazados)}")
    print(f"Registros restantes        : {len(df_limpio)}")
    print(f"Archivo limpio             : {out_limpio.with_suffix('.csv')}")
    print(f"Archivo rechazados         : {out_rechazados.with_suffix('.csv')}")

    return df_limpio, df_rechazados


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: uv run python rechazar_eliminar.py <archivo> <campo> <valor1> [valor2 ...]")
        print("Ejemplo: uv run python rechazar_eliminar.py datos.csv ESTADO Rechazado Eliminado")
        sys.exit(1)

    archivo = sys.argv[1]
    campo = sys.argv[2]
    valores = sys.argv[3:]

    rechazar_eliminar(archivo, campo, valores)
