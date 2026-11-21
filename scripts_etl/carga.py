from pathlib import Path
from decimal import Decimal
from dotenv import load_dotenv
import os
import pandas as pd
import mysql.connector

BASE = Path(__file__).resolve().parents[1]
RESULTADOS = BASE / "datos_resultantes"

load_dotenv(BASE / ".env")


def cargar_datos():

    print("\n|--------------- CARGA ETL ---------------|")

    datos = pd.read_csv(
        RESULTADOS / "violencia_integrada.csv",
        dtype={"codigo_provincia": str}
    )

    print("\n|> LECTURA DEL ARCHIVO INTEGRADO")
    print(f"   Registros disponibles: {len(datos)}")
    print(f"   Atributos: {len(datos.columns)}")

    print("\n|> CONEXIÓN A MYSQL")

    conexion = None
    cursor = None

    try:

        conexion = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            autocommit=False
        )

        cursor = conexion.cursor()

        print("   [OK] Conexión establecida")
        print("   Base de datos: etl_bi")
        print("   Tabla: violencia_homicida")

        consulta = """
            INSERT INTO violencia_homicida (
                codigo_provincia,
                provincia,
                anio,
                poblacion,
                homicidios,
                estado_registro,
                tasa_homicidios_100mil
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        registros = []

        for fila in datos.itertuples(index=False):

            registros.append((
                fila.codigo_provincia,
                fila.provincia,
                int(fila.anio),
                int(fila.poblacion),

                None if pd.isna(fila.homicidios)
                else int(fila.homicidios),

                fila.estado_registro,

                None if pd.isna(fila.tasa_homicidios_100mil)
                else Decimal(str(fila.tasa_homicidios_100mil))
            ))

        print("\n|> INSERCIÓN DE REGISTROS")

        cursor.executemany(consulta, registros)

        print(f"   Registros insertados: {cursor.rowcount}")

        print("\n|> COMPROBACIÓN DE LA CARGA")

        cursor.execute("""
            SELECT COUNT(*)
            FROM violencia_homicida
        """)

        total = cursor.fetchone()[0]

        if total != len(datos):
            raise ValueError("La cantidad de registros no coincide.")

        conexion.commit()

        print(f"   Total almacenado: {total}")
        print("   [OK] Carga confirmada")

    except Exception as error:

        if conexion is not None:
            conexion.rollback()

        print(f"\n   [ERROR] {error}")
        raise

    finally:

        if cursor is not None:
            cursor.close()

        if conexion is not None:
            conexion.close()

        print("\n|> CONEXIÓN CERRADA")

    print("\nCarga ETL finalizada ")


if __name__ == "__main__":
    cargar_datos()