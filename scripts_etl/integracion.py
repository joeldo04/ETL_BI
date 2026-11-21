from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
RESULTADOS = BASE / "datos_resultantes"


def integrar_datos():

    print("\n|------------- INTEGRACIÓN ETL -------------|")

    homicidios = pd.read_csv(
        RESULTADOS / "homicidios_provinciales.csv",
        dtype={"codigo_provincia": str}
    )

    poblacion = pd.read_csv(
        RESULTADOS / "poblacion_provincial.csv",
        dtype={"codigo_provincia": str}
    )

    print("\n|> LECTURA DE ARCHIVOS")
    print(f"   Registros de homicidios: {len(homicidios)}")
    print(f"   Registros poblacionales: {len(poblacion)}")

    datos = poblacion.merge(
        homicidios,
        on=["codigo_provincia", "anio"],
        how="left",
        validate="one_to_one",
        indicator=True
    )

    print("\n|> INTEGRACIÓN DE FUENTES")

    coincidencias = datos["_merge"].eq("both").sum()
    sin_registros = datos["_merge"].eq("left_only").sum()

    print(f"   Registros coincidentes: {coincidencias}")
    print(f"   Registros sin correspondencia: {sin_registros}")

    datos["estado_registro"] = datos["_merge"].map({
        "both": "DISPONIBLE",
        "left_only": "SIN_REGISTROS",
        "right_only": "SIN_POBLACION"
    })

    datos["homicidios"] = datos["homicidios"].astype("Int64")

    datos["tasa_homicidios_100mil"] = (
        datos["homicidios"] / datos["poblacion"] * 100000
    ).round(2)

    datos = datos.drop(columns=["_merge"])

    datos = datos.sort_values(
        ["codigo_provincia", "anio"]
    ).reset_index(drop=True)

    print("\n|> VALIDACIÓN DE RESULTADOS")

    if len(datos) != 48:
        raise ValueError("Cantidad de registros incorrecta.")

    if datos.duplicated(["codigo_provincia", "anio"]).any():
        raise ValueError("Existen claves duplicadas.")

    if datos["homicidios"].sum() != homicidios["homicidios"].sum():
        raise ValueError("Los totales de homicidios no coinciden.")

    print("   [OK] Cantidad de registros")
    print("   [OK] Claves de integración")
    print("   [OK] Totales de homicidios")

    datos.to_csv(
        RESULTADOS / "violencia_integrada.csv",
        index=False,
        encoding="utf-8"
    )

    print("\n|> ARCHIVO GENERADO")
    print("   [OK] violencia_integrada.csv")
    print(f"   Registros: {len(datos)}")
    print(f"   Atributos: {len(datos.columns)}")

    print("\nINTEGRACIÓN FINALIZADA")

    return datos


if __name__ == "__main__":
    integrar_datos()