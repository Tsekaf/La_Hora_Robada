"""
build_html.py - Genera `juego.html` a partir de `historia.json`.

Por que un build step? Para que la historia viva en UN solo lugar
(historia.json) y tanto el motor de consola (motor.py) como la version web
(juego.html) usen exactamente la misma. Si editas la historia, corres:

    python build_html.py

...y el HTML se regenera con la version embebida (no usa fetch, asi el archivo
funciona con doble clic, sin servidor).
"""

import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(DIR, "historia.json"), encoding="utf-8") as f:
    historia = json.load(f)

datos = json.dumps(historia, ensure_ascii=False)

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITULO__</title>
<style>
  :root {
    --bg:#0d1117; --panel:#161b22; --ink:#e6edf3; --muted:#8b949e;
    --accent:#58a6ff; --accent2:#d29922; --line:#30363d; --danger:#f85149;
  }
  * { box-sizing:border-box; }
  body {
    margin:0; min-height:100vh; background:var(--bg); color:var(--ink);
    font-family:Georgia,"Times New Roman",serif;
    display:flex; flex-direction:column; align-items:center;
    padding:24px 16px 60px;
  }
  .wrap { width:100%; max-width:720px; }
  header { text-align:center; margin-bottom:18px; }
  h1 { font-size:1.9rem; letter-spacing:3px; margin:0; color:var(--ink); }
  .sub { color:var(--muted); font-style:italic; margin-top:6px; font-size:.95rem; }
  .hud {
    display:flex; gap:8px; flex-wrap:wrap; justify-content:center;
    margin:14px 0; font-family:ui-monospace,Menlo,monospace; font-size:.78rem;
  }
  .chip { background:var(--panel); border:1px solid var(--line); border-radius:999px;
          padding:4px 12px; color:var(--muted); }
  .chip b { color:var(--accent); }
  .scene {
    background:var(--panel); border:1px solid var(--line); border-radius:12px;
    padding:26px 28px; box-shadow:0 8px 30px rgba(0,0,0,.35);
    animation:fade .5s ease;
  }
  @keyframes fade { from{opacity:0; transform:translateY(8px);} to{opacity:1;} }
  .scene h2 {
    font-size:.8rem; letter-spacing:2px; text-transform:uppercase;
    color:var(--accent2); margin:0 0 16px; border-bottom:1px solid var(--line);
    padding-bottom:10px;
  }
  .scene p { line-height:1.7; margin:0 0 14px; font-size:1.05rem; }
  .choices { margin-top:22px; display:flex; flex-direction:column; gap:10px; }
  button.choice {
    text-align:left; background:transparent; color:var(--ink);
    border:1px solid var(--line); border-radius:8px; padding:14px 16px;
    font-family:inherit; font-size:1rem; cursor:pointer; transition:.15s;
    line-height:1.5;
  }
  button.choice:hover { border-color:var(--accent); background:rgba(88,166,255,.08);
                        transform:translateX(3px); }
  .num { color:var(--accent); font-weight:bold; margin-right:8px; }
  .ending { border-color:var(--accent2); }
  .ending h2 { color:var(--accent2); }
  .endtag { text-align:center; color:var(--accent2); font-style:italic; margin-top:18px;
            letter-spacing:1px; }
  .restart {
    display:block; margin:22px auto 0; background:var(--accent); color:#0d1117;
    border:none; border-radius:8px; padding:12px 26px; font-family:inherit;
    font-weight:bold; font-size:1rem; cursor:pointer;
  }
  .restart:hover { filter:brightness(1.1); }
  footer { color:var(--muted); font-size:.72rem; margin-top:26px; text-align:center; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>__TITULO__</h1>
    <div class="sub">__SUBTITULO__</div>
  </header>
  <div class="hud" id="hud"></div>
  <div id="app"></div>
  <footer>Ficcion interactiva &middot; estado guardado en memoria &middot; v__VERSION__</footer>
</div>

<script>
const HISTORIA = __DATOS__;
const ESCENAS = HISTORIA.escenas;
let estado;

function estadoInicial(){
  const b = HISTORIA.estado_inicial;
  return { lucidez:b.lucidez, confianza:b.confianza, indicios:new Set(b.indicios) };
}

function aplicarEfectos(ef){
  if(!ef) return;
  estado.lucidez   += ef.lucidez   || 0;
  estado.confianza += ef.confianza || 0;
  (ef.indicios||[]).forEach(i => estado.indicios.add(i));
}

function cumple(req){
  if(!req) return true;
  for(const i of (req.indicios||[]))    if(!estado.indicios.has(i)) return false;
  for(const i of (req.indicios_no||[])) if(estado.indicios.has(i))  return false;
  if(req.indicios_alguno && !req.indicios_alguno.some(i=>estado.indicios.has(i))) return false;
  if(req.indicios_min !== undefined && estado.indicios.size < req.indicios_min) return false;
  if(req.lucidez_max   !== undefined && estado.lucidez   > req.lucidez_max)   return false;
  if(req.lucidez_min   !== undefined && estado.lucidez   < req.lucidez_min)   return false;
  if(req.confianza_min !== undefined && estado.confianza < req.confianza_min) return false;
  return true;
}

function renderHud(){
  const inds = [...estado.indicios].sort().join(", ") || "ninguno";
  document.getElementById("hud").innerHTML =
    `<span class="chip">Lucidez <b>${estado.lucidez}</b></span>` +
    `<span class="chip">Confianza <b>${estado.confianza}</b></span>` +
    `<span class="chip">Indicios: ${inds}</span>`;
}

function parrafos(texto){
  return texto.split("\\n").filter(l=>l.trim()!=="")
              .map(l=>`<p>${l}</p>`).join("");
}

function mostrar(id){
  const esc = ESCENAS[id];
  aplicarEfectos(esc.efectos);
  renderHud();

  const app = document.getElementById("app");
  const esFinal = !!esc.final;
  let html = `<div class="scene ${esFinal?'ending':''}">`;
  html += `<h2>${esc.titulo}</h2>`;
  html += parrafos(esc.texto);

  if(esFinal){
    html += `<div class="endtag">Final: ${esc.tipo_final}</div>`;
    html += `<button class="restart" onclick="iniciar()">Jugar de nuevo</button>`;
    html += `</div>`;
    app.innerHTML = html;
    return;
  }

  const opts = esc.opciones.filter(o => cumple(o.requiere));
  html += `<div class="choices">`;
  opts.forEach((o,i) => {
    html += `<button class="choice" data-i="${i}">`+
            `<span class="num">${i+1}</span>${o.texto}</button>`;
  });
  html += `</div></div>`;
  app.innerHTML = html;

  app.querySelectorAll("button.choice").forEach(btn => {
    btn.addEventListener("click", () => {
      const o = opts[parseInt(btn.dataset.i,10)];
      aplicarEfectos(o.efectos);
      window.scrollTo({top:0, behavior:"smooth"});
      mostrar(o.destino);
    });
  });
}

function iniciar(){
  estado = estadoInicial();
  window.scrollTo({top:0});
  mostrar(HISTORIA.inicio);
}

iniciar();
</script>
</body>
</html>
"""

html = (HTML
        .replace("__TITULO__", historia["meta"]["titulo"])
        .replace("__SUBTITULO__", historia["meta"]["subtitulo"])
        .replace("__VERSION__", historia["meta"].get("version", "1.0"))
        .replace("__DATOS__", datos))

with open(os.path.join(DIR, "juego.html"), "w", encoding="utf-8") as f:
    f.write(html)

print("juego.html generado OK (" + str(len(html)) + " bytes)")
