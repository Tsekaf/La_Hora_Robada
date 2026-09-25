"""
LA HORA ROBADA - Motor de ficcion interactiva (version consola)
================================================================

Este archivo es el "motor" (engine): no contiene la historia, solo la logica
para recorrerla. La historia vive en `historia.json`, que es la UNICA fuente de
verdad. Asi separamos DATOS (la historia) de LOGICA (como se juega), que es la
misma idea que usa la version HTML.

Modelo mental:
  - El juego es un GRAFO DIRIGIDO. Cada "escena" es un nodo; cada "opcion" es una
    arista que apunta a otra escena (campo `destino`).
  - El ESTADO del jugador es un diccionario: lucidez (int), confianza (int) e
    indicios (un conjunto de flags de texto). Las elecciones aplican `efectos`
    que modifican ese estado.
  - Algunas opciones tienen `requiere`: solo se muestran si el estado cumple la
    condicion. Asi un mismo nodo (el climax) abre finales distintos segun lo que
    hiciste antes. Eso es lo que da la sensacion de "yo arme esta historia".

Como se juega:
    python motor.py
"""

import json
import os
import textwrap

# --- Carga de datos -------------------------------------------------------

# Buscamos historia.json en la misma carpeta que este script, para que ande
# sin importar desde donde se ejecute.
RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "historia.json")

with open(RUTA, encoding="utf-8") as f:
    HISTORIA = json.load(f)

ESCENAS = HISTORIA["escenas"]


# --- Logica de estado -----------------------------------------------------

def estado_inicial():
    """Devuelve una copia fresca del estado para poder reiniciar la partida."""
    base = HISTORIA["estado_inicial"]
    return {
        "lucidez": base["lucidez"],
        "confianza": base["confianza"],
        "indicios": set(base["indicios"]),  # usamos un set: orden no importa, no hay duplicados
    }


def aplicar_efectos(estado, efectos):
    """Modifica el estado en el lugar segun el bloque `efectos` de una escena u opcion."""
    if not efectos:
        return
    estado["lucidez"] += efectos.get("lucidez", 0)
    estado["confianza"] += efectos.get("confianza", 0)
    for indicio in efectos.get("indicios", []):
        estado["indicios"].add(indicio)


def cumple_requisito(estado, requiere):
    """True si el estado actual habilita una opcion. Sin `requiere`, siempre True."""
    if not requiere:
        return True
    # Todos los indicios pedidos tienen que estar presentes (AND).
    for ind in requiere.get("indicios", []):
        if ind not in estado["indicios"]:
            return False
    # Ningun indicio "prohibido" puede estar presente.
    for ind in requiere.get("indicios_no", []):
        if ind in estado["indicios"]:
            return False
    # Al menos uno de la lista (OR).
    alguno = requiere.get("indicios_alguno")
    if alguno and not any(ind in estado["indicios"] for ind in alguno):
        return False
    # Cantidad minima de indicios juntados.
    if "indicios_min" in requiere and len(estado["indicios"]) < requiere["indicios_min"]:
        return False
    # Cotas sobre los stats numericos.
    if "lucidez_max" in requiere and estado["lucidez"] > requiere["lucidez_max"]:
        return False
    if "lucidez_min" in requiere and estado["lucidez"] < requiere["lucidez_min"]:
        return False
    if "confianza_min" in requiere and estado["confianza"] < requiere["confianza_min"]:
        return False
    return True


# --- Presentacion ---------------------------------------------------------

ANCHO = 78

def parrafo(texto):
    """Imprime texto justificado a un ancho fijo, respetando los saltos de linea."""
    for linea in texto.split("\n"):
        if linea.strip() == "":
            print()
        else:
            print(textwrap.fill(linea, width=ANCHO))


def barra_estado(estado):
    inds = ", ".join(sorted(estado["indicios"])) or "ninguno"
    return f"[ Lucidez: {estado['lucidez']}  |  Confianza: {estado['confianza']}  |  Indicios: {inds} ]"


# --- Bucle principal ------------------------------------------------------

def jugar():
    print("=" * ANCHO)
    print(HISTORIA["meta"]["titulo"].center(ANCHO))
    print(HISTORIA["meta"]["subtitulo"].center(ANCHO))
    print("=" * ANCHO)
    input("\n(Enter para empezar)")

    estado = estado_inicial()
    actual = HISTORIA["inicio"]

    while True:
        escena = ESCENAS[actual]

        # 1) Al entrar a una escena, aplicamos sus efectos (una sola vez).
        aplicar_efectos(estado, escena.get("efectos"))

        # 2) Mostramos la escena.
        print("\n" + "-" * ANCHO)
        print(escena["titulo"].upper())
        print("-" * ANCHO + "\n")
        parrafo(escena["texto"])

        # 3) Si es un final, terminamos.
        if escena.get("final"):
            print("\n" + "=" * ANCHO)
            print(f"  Final alcanzado: {escena['tipo_final']}".center(ANCHO))
            print(barra_estado(estado).center(ANCHO))
            print("=" * ANCHO)
            if input("\nJugar de nuevo? (s/n) ").strip().lower() == "s":
                estado = estado_inicial()
                actual = HISTORIA["inicio"]
                continue
            print("\nGracias por jugar.")
            return

        # 4) Filtramos las opciones disponibles segun el estado.
        print("\n" + barra_estado(estado))
        disponibles = [op for op in escena["opciones"] if cumple_requisito(estado, op.get("requiere"))]

        print()
        for i, op in enumerate(disponibles, start=1):
            print(textwrap.fill(f"  {i}) {op['texto']}", width=ANCHO, subsequent_indent="     "))

        # 5) Pedimos una eleccion valida.
        eleccion = pedir_eleccion(len(disponibles))
        op = disponibles[eleccion - 1]

        # 6) Aplicamos los efectos de la opcion elegida y avanzamos.
        aplicar_efectos(estado, op.get("efectos"))
        actual = op["destino"]


def pedir_eleccion(n):
    """Lee de teclado hasta que el usuario ingrese un numero entre 1 y n."""
    while True:
        entrada = input("\n> Tu eleccion: ").strip()
        if entrada.isdigit() and 1 <= int(entrada) <= n:
            return int(entrada)
        print(f"  (Escribi un numero del 1 al {n}.)")


if __name__ == "__main__":
    try:
        jugar()
    except (KeyboardInterrupt, EOFError):
        print("\n\nPartida interrumpida. Hasta la proxima.")
