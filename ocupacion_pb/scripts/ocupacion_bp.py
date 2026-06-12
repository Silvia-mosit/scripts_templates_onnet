import sys
import pandas as pd
from pathlib import Path

CSV_PATH = "../data_general/actualizacion/Recursos_OLT_Ocupacion_20260611_PENCO.csv"
OLT_PATH = "../data_general/Consolidado_OLT.xlsx"


def _output_path(csv_path: str) -> str:
    p = Path(csv_path)
    return str(p.with_stem(p.stem + "_output"))


def agregar_modelo_homologado(df_recursos: pd.DataFrame, df_olt: pd.DataFrame) -> pd.DataFrame:
    mapa = df_olt.set_index("IPADDRESS")["MODELO_HOMOLOGADO(BP)"]
    df_recursos["MODELO_HOMOLOGADO_BP"] = df_recursos["IPADDRESS"].map(mapa)
    return df_recursos



def validar_ips(df_recursos: pd.DataFrame, df_olt: pd.DataFrame) -> None:
    ips_recursos = set(df_olt["IPADDRESS"].dropna().unique())
    for ip in df_recursos["IPADDRESS"].dropna().unique():
        if ip in ips_recursos:
            print(f"[OK]  IP encontrada: {ip}")
        else:
            print(f"[NOK] IP NO encontrada: {ip}")


def procesar(csv_path: str = CSV_PATH, olt_path: str = OLT_PATH, guardar: bool = True) -> pd.DataFrame:
    df = pd.read_csv(csv_path, sep=None, engine="python")
    df_olt = pd.read_excel(olt_path)

    df = agregar_modelo_homologado(df, df_olt)

    print("=== Validacion de IPs ===")
    validar_ips(df, df_olt)

    df["MODELO"] = df["MODELO_HOMOLOGADO_BP"]
    df = df.drop(columns=["MODELO_HOMOLOGADO_BP"])

    print("\n=== Primeras 10 filas del df resultante ===")
    print(df.head(10).to_string())

    if guardar:
        out = _output_path(csv_path)
        df.to_csv(out, sep=";", index=False)
        print(f"\nArchivo generado: {out}")

    return df


if __name__ == "__main__":
    csv = sys.argv[1] if len(sys.argv) > 1 else CSV_PATH
    olt = sys.argv[2] if len(sys.argv) > 2 else OLT_PATH
    procesar(csv, olt)
