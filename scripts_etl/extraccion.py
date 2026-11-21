from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

BASE = Path(__file__).resolve().parents[1]
FUENTES = BASE / "datos_fuente"


def leer_homicidios(archivo):
    libro = load_workbook(
        archivo,
        read_only=True,
        data_only=True
    )

    try:
        hoja = libro["1. Homicidios Intencionales"]
        hoja.reset_dimensions()

        filas = hoja.values
        columnas = next(filas)

        datos = [
            fila for fila in filas
            if any(valor is not None for valor in fila)
        ]

        return pd.DataFrame(datos, columns=columnas)

    finally:
        libro.close()


def extraer_datos():
    historico = leer_homicidios(
        FUENTES / "mdi_homicidiosintencionalse_pm_2014_2025.xlsx"
    )

    actual = leer_homicidios(
        FUENTES / "mdi_homicidiosintencionales_pm_2026_enero_octubre.xlsx"
    )

    poblacion = pd.read_excel(
        FUENTES / "Tabulados_Estimacion_Proyeccion_v2.xlsx",
        sheet_name="2.3",
        header=None,
        skiprows=15,
        nrows=144,
        usecols="B:D,DH,DK",
        dtype=str
    )

    poblacion.columns = [
        "codigo_provincia",
        "provincia",
        "etapa_vida",
        "poblacion_2025",
        "poblacion_2026"
    ]

    return historico, actual, poblacion


if __name__ == "__main__":
    historico, actual, poblacion = extraer_datos()

    fuentes = {
        "Homicidios 2014-2025": historico,
        "Homicidios 2026": actual,
        "Proyecciones poblacionales": poblacion
    }

    print("\n|> EXTRACCIÓN DE DATOS \n")

    for nombre, datos in fuentes.items():
        print(f"Fuente: {nombre}")
        print(f"Registros: {len(datos)}")
        print(f"Atributos: {len(datos.columns)}")
        print("-" * 45)

    print("\nExtracción finalizada correctamente.")