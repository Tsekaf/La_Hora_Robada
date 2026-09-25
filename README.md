# La hora robada

Ficción interactiva (detective + sobrenatural). Ver [LEEME.md](LEEME.md) para la
historia, el modelo de datos y cómo extenderla.

## Cómo jugarlo

Doble clic en `juego.html`. No necesita servidor ni conexión: la historia va
embebida en el archivo.

## Nota sobre las herramientas en Python

`motor.py` (versión consola) y `build_html.py` (regenera `juego.html` desde
`historia.json`) **no corren en esta máquina**: no hay un Python real instalado,
sólo el acceso directo de Microsoft Store.

Eso no afecta a jugar — `juego.html` ya está generado y es autónomo. Sólo importa
si querés editar `historia.json` y regenerar el HTML: para eso hace falta instalar
Python desde <https://python.org> y correr `python build_html.py`.

## Estado

Terminado y verificado: 23 escenas, 6 finales, sin destinos rotos ni escenas
inalcanzables.

## Si lo publicás en GitHub Pages

Pages sirve `index.html` en la raíz, y acá el juego se llama `juego.html`. O sea
que el link va a ser:

```
https://TU-USUARIO.github.io/la-hora-robada/juego.html
```

y la raíz (sin `/juego.html`) va a dar 404.

Si preferís el link limpio, renombrá el archivo y ajustá las dos referencias:

```bash
git mv juego.html index.html
sed -i 's/juego\.html/index.html/g' build_html.py LEEME.md README.md
```

(`build_html.py` genera ese archivo, por eso hay que tocarlo también: si no, la
próxima vez que lo corras te vuelve a escribir `juego.html` y quedan los dos.)
