Instrucciones por tramo para generacion de templates:

Tramo 11:
paso 1: Buscar codigo en ingresas_codigo_cable.py. Esto busca el codigo de acuerdo 
al numero de referencia (template t11, columna M identificación del objeto)
en el array del script. El archivo de salida es el mismo con la columna O 
con el código correspondiente. Una vez obtenido, borrar identificador.

2: Obtener row_num desde buscar_row_num.py. Se busca en t14/t14_DGO_inicial_general_ultimo,
col W, si ese codigo existe en la columna H codigo de t11.xlsx
La salida es t11.xlsx, columna row_num BV.

Tramo 10:
*En data_general_t10 CTO es para acceso y mufas para empalme
paso 1: Buscar por los codigos OLT de una zona especifica (por ej. buin_olt ) en el archivo
t10_data_general, de acuerdo a si es acceso o empalme. Esto se hace con filtrar_por_codigos.py

paso 2: Con buscar_puertos_preferenciales.py, buscar puertos preferenciales, el row_num de la primera hoja del archivo final t10 se busca en el archivo
t10_puertos_preferenciales_completo, en las hojas  1 y 2.

paso 3: Buscar divisor optico, el mismo paso 2 pero con el archivo de datos 
T10_divisor_acceso segun empalme o acceso.


Tramo 14:
