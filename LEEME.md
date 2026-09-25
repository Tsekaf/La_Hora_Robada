# LA HORA ROBADA — ficción interactiva

Detective + sobrenatural. Investigás la muerte de Elena Var: el forense fija la hora
a las 21:00, pero tres testigos la vieron viva a las 23:40. Tres actos, 23 escenas,
**6 finales** (Sacrificio, Corrupción, Racional, Trágico, Liberación, Intercambio).

## Cómo jugar

- **Navegador (recomendado):** doble clic en `juego.html`. No instala nada, no necesita servidor.
- **Consola (Python):** `python motor.py`

## Archivos y por qué están separados

| Archivo | Rol |
|---|---|
| `historia.json` | **Los datos**: la historia entera como grafo de escenas. Única fuente de verdad. |
| `motor.py` | **La lógica** en Python: lee el JSON y corre el juego en consola. Comentado. |
| `build_html.py` | Genera `juego.html` inyectando el JSON. Corré esto si editás la historia. |
| `juego.html` | La versión jugable en navegador (con el JSON ya embebido). |

La idea clave (que vale para cualquier motor de este tipo): **separar datos de lógica**.
La historia no sabe nada de cómo se dibuja; el motor no sabe nada de qué pasa en la trama.
Por eso el mismo `historia.json` alimenta tanto la consola como el HTML.

## El "estado" del jugador

Tres variables deciden qué ramas se abren:

- **lucidez** — qué tan anclado estás a la explicación racional. Baja al aceptar lo extraño.
- **confianza** — tu vínculo con la inspectora Vega.
- **indicios** — flags de texto (`reloj`, `carta`, `trato`, `gemela`, `vega`).

Cada opción aplica `efectos` (modifican el estado) y puede tener `requiere` (solo aparece
si el estado lo cumple). Por eso el final depende de cómo investigaste, no de un botón final.

## Cómo extender la historia

1. Editás `historia.json`: agregás una escena nueva al objeto `escenas` y la apuntás desde
   alguna `opcion` con `destino`.
2. Corrés `python build_html.py` para regenerar el HTML.
3. (Opcional) Corrés el verificador para chequear que no haya destinos rotos ni finales
   inalcanzables.

### Esquema de una escena

```json
"id_escena": {
  "titulo": "...",
  "texto": "Párrafos separados por \n.",
  "efectos": { "lucidez": -1, "confianza": 1, "indicios": ["reloj"] },
  "opciones": [
    {
      "texto": "Lo que ve el jugador",
      "destino": "id_otra_escena",
      "efectos": { "indicios": ["carta"] },
      "requiere": { "indicios": ["trato"], "indicios_no": ["vega"], "lucidez_max": 2 }
    }
  ]
}
```

### Operadores de `requiere`

| Clave | Significado |
|---|---|
| `indicios` | Deben estar **todos** (AND). |
| `indicios_no` | No debe estar **ninguno**. |
| `indicios_alguno` | Debe estar **al menos uno** (OR). |
| `indicios_min` | Mínimo de indicios juntados (número). |
| `lucidez_max` / `lucidez_min` | Cota sobre la lucidez. |
| `confianza_min` | Mínimo de confianza. |

Los indicios que empiezan con `v_` (ej. `v_testigos`) son **marcadores internos**: sirven
para que una escena ya visitada desaparezca del menú. No son pistas de la trama.

Para un **final**: poné `"final": true`, `"tipo_final": "..."` y `"opciones": []`.

> Nota de diseño: los "hubs" (`ciudad`, `encrucijada`) no modifican stats al entrar, así
> que se pueden revisitar sin efectos secundarios. Las ubicaciones que sí dan pistas se
> bloquean con su marcador `v_*`, de modo que cada una se visita una sola vez.

## Compartirlo con otras personas

`juego.html` es **un solo archivo autocontenido** (la historia va embebida, no usa
internet ni servidor). Para que lo prueben tenés dos caminos:

1. **Mandar el archivo** (mail, WhatsApp, Drive). Quien lo reciba lo abre con doble clic
   en cualquier compu o celular. Funciona offline. Es lo más rápido.
2. **Publicarlo y tener un link real** (gratis): subí `juego.html` a *itch.io* (ideal para
   juegos de texto), *Netlify Drop* (arrastrás el archivo y te da una URL) o *GitHub Pages*.
   Ahí sí obtenés un link que cualquiera abre en el navegador.

Un "link" propiamente dicho solo existe si el archivo está alojado en algún lado (opción 2);
si no, lo que compartís es el archivo en sí (opción 1).
