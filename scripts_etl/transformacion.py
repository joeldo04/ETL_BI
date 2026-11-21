from pathlib import Path
import pandas as pd
from extraccion import extraer_datos

BASE = Path(__file__).resolve().parents[1]
RESULTADOS = BASE / "datos_resultantes"


def normalizar_codigo(columna):
    return columna.astype("string").str.strip().str.zfill(2)


def transformar_homicidios(historico, actual):

    print("\n|> PROCESAMIENTO DE HOMICIDIOS")

    datos = pd.concat([historico, actual], ignore_index=True)

    datos["fecha_infraccion"] = pd.to_datetime(
        datos["fecha_infraccion"], errors="coerce"
    )

    if datos["fecha_infraccion"].isna().any():
        raise ValueError("Existen fechas faltantes o inválidas.")

    datos["anio"] = datos["fecha_infraccion"].dt.year
    datos["mes"] = datos["fecha_infraccion"].dt.month

    datos = datos.loc[
        datos["anio"].isin([2025, 2026])
        & datos["mes"].le(10)
    ].copy()

    duplicados = datos.duplicated().sum()

    print(f"   Filas idénticas adicionales: {duplicados}")
    print("   Periodo seleccionado: Enero - Octubre")

    # Se conservan los registros idénticos porque
    # no existe un identificador único de víctima

    datos["codigo_provincia"] = normalizar_codigo(
        datos["codigo_provincia"]
    )

    codigos_validos = [f"{n:02d}" for n in range(1, 25)]

    if not datos["codigo_provincia"].isin(codigos_validos).all():
        raise ValueError("Existen códigos provinciales inválidos.")

    resumen = (
        datos.groupby(["codigo_provincia", "anio"])
        .size()
        .reset_index(name="homicidios")
    )

    if resumen["homicidios"].sum() != len(datos):
        raise ValueError("Los totales no coinciden.")

    print(f"   Registros agrupados: {len(resumen)}")
    print("   [OK] Transformación de homicidios")

    return resumen


def transformar_poblacion(poblacion):

    print("\n|> PROCESAMIENTO DE POBLACIÓN")

    datos = poblacion.loc[
        poblacion["etapa_vida"].str.strip().str.upper().eq("TOTAL")
    ].copy()

    datos["codigo_provincia"] = normalizar_codigo(
        datos["codigo_provincia"]
    )

    datos["provincia"] = datos["provincia"].str.strip()

    datos = datos.melt(
        id_vars=["codigo_provincia", "provincia"],
        value_vars=["poblacion_2025", "poblacion_2026"],
        var_name="anio",
        value_name="poblacion"
    )

    datos["anio"] = datos["anio"].map({
        "poblacion_2025": 2025,
        "poblacion_2026": 2026
    })

    datos["poblacion"] = pd.to_numeric(
        datos["poblacion"], errors="raise"
    )

    if datos["poblacion"].isna().any() or (datos["poblacion"] <= 0).any():
        raise ValueError("Existen valores poblacionales inválidos.")

    if datos.duplicated(["codigo_provincia", "anio"]).any():
        raise ValueError("Existen claves poblacionales duplicadas.")

    codigos_validos = {f"{n:02d}" for n in range(1, 25)}

    if len(datos) != 48 or set(datos["codigo_provincia"]) != codigos_validos:
        raise ValueError("La cobertura poblacional no es la esperada.")

    datos = datos.sort_values(
        ["codigo_provincia", "anio"]
    ).reset_index(drop=True)

    print(f"   Provincias: {datos['codigo_provincia'].nunique()}")
    print(f"   Registros transformados: {len(datos)}")
    print("   [OK] Transformación poblacional")

    return datos


def transformar_datos(historico, actual, poblacion):

    homicidios = transformar_homicidios(historico, actual)
    proyecciones = transformar_poblacion(poblacion)

    return homicidios, proyecciones


if __name__ == "__main__":

    print("\n|------------- TRANSFORMACIÓN ETL -------------|")

    historico, actual, poblacion = extraer_datos()

    homicidios, proyecciones = transformar_datos(
        historico, actual, poblacion
    )

    RESULTADOS.mkdir(parents=True, exist_ok=True)

    homicidios.to_csv(
        RESULTADOS / "homicidios_provinciales.csv", index=False
    )

    proyecciones.to_csv(
        RESULTADOS / "poblacion_provincial.csv", index=False
    )

    print("\n|> RESUMEN DE HOMICIDIOS")

    for anio, total in homicidios.groupby("anio")["homicidios"].sum().items():
        print(f"   Homicidios {anio}: {total}")

    print("\n|> ARCHIVOS GENERADOS")
    print("   [OK] homicidios_provinciales.csv")
    print("   [OK] poblacion_provincial.csv")

    print("\n|---------- TRANSFORMACIÓN FINALIZADA ----------|")