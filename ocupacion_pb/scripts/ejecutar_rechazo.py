import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from rechazar_eliminar import rechazar_eliminar

BASE = Path(__file__).parents[1] / "data_general/actualizacion/finales"

CSV = BASE / "Recursos_OLT_Ocupacion_OLT-TEMUCOPONIENTE_OLD_key.csv"
XLSX = BASE / "rechazados_temuco_keys.xlsx"

xls = pd.read_excel(XLSX)
valores = xls["LLAVE"].dropna().astype(str).tolist()
print(f"Valores a rechazar: {len(valores)}")

rechazar_eliminar(archivo=str(CSV), campo="KEY", valores=valores)
