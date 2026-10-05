"""
Método de Bisección animado
===========================

Encuentra una raíz de f(x) en [a, b] partiendo el intervalo a la mitad en cada
iteración, y lo anima: vista global de la función, una cámara que hace zoom
siguiendo al intervalo y la gráfica de convergencia del error.

Requisitos:  pip install numpy matplotlib
             (para guardar .mp4 hace falta ffmpeg; para .gif basta pillow)

Uso:         edita la sección INPUTS y ejecuta  python biseccion.py
"""

# ═══════════════════════════════════ INPUTS ═══════════════════════════════════

# f(x) como texto. Variable: x. Potencia: ** o ^.
# Funciones: sin cos tan asin acos atan sinh cosh tanh exp log (=ln) log10 log2
#            sqrt cbrt abs floor ceil sign   ·   constantes: pi, e
# El dominio son los reales: donde f no sea real (p. ej. sqrt(-1)) vale NaN.
FUNCION = "x**3 - 2*x - 5"

A = 1.0                 # extremo izquierdo del intervalo
B = 3.0                 # extremo derecho del intervalo  (f(A) y f(B) con signos opuestos)

TOLERANCIA = 1e-6       # se detiene cuando el error |b - a| / 2 < TOLERANCIA
MAX_ITERACIONES = 60

DURACION = 10.0         # segundos que tarda la animación en converger
FPS = 30                # cuadros por segundo
PAUSA_FINAL = 2.5       # segundos mostrando el resultado al terminar

GUARDAR_COMO = ""       # "" = abrir ventana  ·  "biseccion.mp4" o "biseccion.gif" = guardar archivo

# ══════════════════════════════════ CÓDIGO ════════════════════════════════════

import math

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle
from matplotlib.ticker import ScalarFormatter
from matplotlib.transforms import blended_transform_factory

COLOR = {
    "fondo": "#0d1021",
    "panel": "#141832",
    "rejilla": "#232849",
    "texto": "#dde1f5",
    "tenue": "#7c83a9",
    "curva": "#7aa2ff",
    "a": "#ff6b8b",
    "b": "#4fd1c5",
    "c": "#ffd166",
    "raiz": "#b8f27c",
    "error": "#c792ea",
}

plt.rcParams.update({
    "figure.facecolor": COLOR["fondo"],
    "axes.facecolor": COLOR["panel"],
    "axes.edgecolor": COLOR["rejilla"],
    "axes.labelcolor": COLOR["tenue"],
    "axes.titlecolor": COLOR["texto"],
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "axes.grid": True,
    "grid.color": COLOR["rejilla"],
    "grid.linewidth": 0.6,
    "xtick.color": COLOR["tenue"],
    "ytick.color": COLOR["tenue"],
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "text.color": COLOR["texto"],
    "font.family": "DejaVu Sans",
    "legend.frameon": False,
    "legend.fontsize": 8,
    "legend.labelcolor": COLOR["texto"],
})

FUNCIONES_PERMITIDAS = {
    "sin": np.sin, "cos": np.cos, "tan": np.tan,
    "asin": np.arcsin, "acos": np.arccos, "atan": np.arctan,
    "arcsin": np.arcsin, "arccos": np.arccos, "arctan": np.arctan,
    "sinh": np.sinh, "cosh": np.cosh, "tanh": np.tanh,
    "exp": np.exp, "log": np.log, "ln": np.log, "log10": np.log10, "log2": np.log2,
    "sqrt": np.sqrt, "cbrt": np.cbrt, "abs": np.abs,
    "floor": np.floor, "ceil": np.ceil, "sign": np.sign,
    "pi": np.pi, "e": np.e,
}


def construir_funcion(expresion):
    """Convierte el texto en una función real vectorizada; fuera del dominio real devuelve NaN."""
    codigo = compile(expresion.replace("^", "**"), "<f(x)>", "eval")
    desconocidos = [n for n in codigo.co_names if n != "x" and n not in FUNCIONES_PERMITIDAS]
    if desconocidos:
        raise ValueError(f"Nombres no reconocidos en f(x): {', '.join(desconocidos)}")

    def f(x):
        x = np.asarray(x, dtype=float)
        with np.errstate(all="ignore"):
            y = eval(codigo, {"__builtins__": {}}, {**FUNCIONES_PERMITIDAS, "x": x})
        if np.iscomplexobj(y):
            raise ValueError("f(x) debe ser real (no uses números complejos como 1j)")
        y = np.broadcast_to(np.asarray(y, dtype=float), x.shape).copy()
        y[~np.isfinite(y)] = np.nan
        return y if y.ndim else float(y)

    return f


def biseccion(f, a, b, tol, max_iter):
    """Devuelve la lista de pasos: intervalo antes y después de cada iteración."""
    fa, fb = f(a), f(b)
    if math.isnan(fa) or math.isnan(fb):
        raise ValueError(f"f no está definida en los reales en {'a' if math.isnan(fa) else 'b'}")
    if fa * fb > 0:
        raise ValueError(f"f(a) = {fa:.4g} y f(b) = {fb:.4g} tienen el mismo signo: "
                         "el intervalo no encierra un cambio de signo")

    pasos = []
    for k in range(1, max_iter + 1):
        c = a + (b - a) / 2
        fc = f(c)
        if math.isnan(fc):
            raise ValueError(f"f no está definida en los reales en x = {c:.8g}")

        if fc == 0:
            a2, b2, fa2, fb2 = c, c, fc, fc
        elif np.sign(fa) * np.sign(fc) < 0:
            a2, b2, fa2, fb2 = a, c, fa, fc
        else:
            a2, b2, fa2, fb2 = c, b, fc, fb

        pasos.append(dict(k=k, a=a, b=b, c=c, fc=fc, a2=a2, b2=b2,
                          descarta="nada" if fc == 0 else ("der" if b2 == c else "izq")))
        a, b, fa, fb = a2, b2, fa2, fb2
        if fc == 0 or (b - a) / 2 < tol:
            break
    return pasos


def suavizar(t):
    """Easing cúbico de entrada y salida, t en [0, 1]."""
    t = min(max(t, 0.0), 1.0)
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def curva_con_brillo(ax, color, z=3):
    """Línea con halo: varias capas anchas y translúcidas debajo de la línea principal."""
    capas = [ax.plot([], [], color=color, lw=lw, alpha=al, solid_capstyle="round", zorder=z)[0]
             for lw, al in ((9, 0.05), (5, 0.10), (3, 0.25))]
    capas.append(ax.plot([], [], color=color, lw=1.8, zorder=z + 0.1)[0])
    return capas


def punto(ax, color, tam=8, z=6):
    return ax.plot([], [], "o", ms=tam, color=color, mec="white", mew=1.2, zorder=z,
                   path_effects=[pe.withStroke(linewidth=6, foreground=color, alpha=0.25)])[0]


def main():
    f = construir_funcion(FUNCION)
    a0, b0 = min(A, B), max(A, B)

    fa0, fb0 = f(a0), f(b0)
    if fa0 == 0 or fb0 == 0:
        print(f"Un extremo ya es raíz: x = {a0 if fa0 == 0 else b0}")
        return

    pasos = biseccion(f, a0, b0, TOLERANCIA, MAX_ITERACIONES)
    n = len(pasos)
    raiz = pasos[-1]["c"]
    ancho0 = b0 - a0
    decimales = max(6, math.ceil(-math.log10(TOLERANCIA)) + 2)

    print(f"Raíz ≈ {raiz:.{decimales}f}   ·   f(raíz) = {pasos[-1]['fc']:.3e}   ·   {n} iteraciones")

    # ── Figura ────────────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(13, 8))
    rejilla = fig.add_gridspec(2, 2, height_ratios=[1.25, 1], width_ratios=[1.35, 1],
                               left=0.06, right=0.97, top=0.88, bottom=0.08, hspace=0.32, wspace=0.18)
    ax_g = fig.add_subplot(rejilla[0, :])
    ax_z = fig.add_subplot(rejilla[1, 0])
    ax_e = fig.add_subplot(rejilla[1, 1])

    fig.text(0.06, 0.95, "Método de Bisección", fontsize=20, weight="bold", color=COLOR["texto"])
    fig.text(0.06, 0.915, f"f(x) = {FUNCION}     ·     [a, b] = [{a0:g}, {b0:g}]     ·     "
             f"tolerancia = {TOLERANCIA:g}", fontsize=10.5, color=COLOR["tenue"])

    # Vista global (fija)
    margen = 0.12 * ancho0
    xs_g = np.linspace(a0 - margen, b0 + margen, 1200)
    ys_g = f(xs_g)
    ax_g.set_title("Vista global")
    ax_g.set_xlim(xs_g[0], xs_g[-1])
    finitos = ys_g[np.isfinite(ys_g)]
    y_lo, y_hi = min(finitos.min(), 0), max(finitos.max(), 0)
    ax_g.set_ylim(y_lo - 0.12 * (y_hi - y_lo), y_hi + 0.12 * (y_hi - y_lo))
    for capa in curva_con_brillo(ax_g, COLOR["curva"]):
        capa.set_data(xs_g, ys_g)
    ax_g.axhline(0, color=COLOR["tenue"], lw=0.9, alpha=0.7, zorder=2)

    # Vista con zoom (la cámara sigue al intervalo)
    ax_z.set_title("Zoom sobre el intervalo")
    ax_z.axhline(0, color=COLOR["tenue"], lw=0.9, alpha=0.7, zorder=2)
    curva_z = curva_con_brillo(ax_z, COLOR["curva"])
    for eje in (ax_z.xaxis, ax_z.yaxis):
        formato = ScalarFormatter(useOffset=True, useMathText=True)
        formato.set_powerlimits((-3, 4))
        eje.set_major_formatter(formato)
        eje.get_offset_text().set_color(COLOR["tenue"])
        eje.get_offset_text().set_fontsize(8)

    # Elementos animados que existen en ambas vistas
    elementos = []
    for ax in (ax_g, ax_z):
        trans = blended_transform_factory(ax.transData, ax.transAxes)
        e = dict(
            intervalo=Rectangle((0, 0), 0, 1, transform=trans, color=COLOR["c"], alpha=0.09, zorder=1),
            descarte=Rectangle((0, 0), 0, 1, transform=trans, color=COLOR["a"], alpha=0, zorder=1),
            linea_a=ax.axvline(0, color=COLOR["a"], lw=1.2, ls="--", alpha=0.8, zorder=2),
            linea_b=ax.axvline(0, color=COLOR["b"], lw=1.2, ls="--", alpha=0.8, zorder=2),
            tallo=ax.plot([], [], color=COLOR["c"], lw=1.6, ls=":", zorder=4)[0],
            pa=punto(ax, COLOR["a"]),
            pb=punto(ax, COLOR["b"]),
            pc=punto(ax, COLOR["c"], tam=9, z=7),
            raiz=ax.plot([], [], "*", ms=20, color=COLOR["raiz"], mec="white", mew=1, zorder=8,
                         path_effects=[pe.withStroke(linewidth=10, foreground=COLOR["raiz"], alpha=0.3)])[0],
        )
        ax.add_patch(e["intervalo"])
        ax.add_patch(e["descarte"])
        elementos.append(e)
    elementos[0]["pa"].set_label("a")
    elementos[0]["pb"].set_label("b")
    elementos[0]["pc"].set_label("c = (a + b) / 2")
    ax_g.legend(loc="lower right", ncol=3)

    info = ax_g.text(0.012, 0.95, "", transform=ax_g.transAxes, va="top", ha="left", family="monospace",
                     fontsize=9.5, zorder=10,
                     bbox=dict(boxstyle="round,pad=0.6", fc=COLOR["fondo"], ec=COLOR["rejilla"], alpha=0.88))

    # Convergencia
    ks = np.array([p["k"] for p in pasos])
    err = np.array([(p["b"] - p["a"]) / 2 for p in pasos])
    res = np.array([max(abs(p["fc"]), 1e-17) for p in pasos])
    ax_e.set_title("Convergencia")
    ax_e.set_yscale("log")
    ax_e.set_xlim(0.5, max(n, 2) + 0.5)
    ax_e.set_ylim(min(err.min(), res.min(), TOLERANCIA) / 8, max(err.max(), res.max()) * 8)
    ax_e.set_xlabel("iteración")
    ax_e.axhline(TOLERANCIA, color=COLOR["raiz"], lw=1, ls="--", alpha=0.7, label="tolerancia")
    linea_err = ax_e.plot([], [], "-o", color=COLOR["error"], ms=4, lw=1.8, label="error  |b − a| / 2")[0]
    linea_res = ax_e.plot([], [], "-s", color=COLOR["c"], ms=3.5, lw=1.2, alpha=0.85, label="|f(c)|")[0]
    ax_e.legend(loc="lower left")

    # ── Línea de tiempo ───────────────────────────────────────────────────────
    cuadros_conv = max(1, round(DURACION * FPS))
    cuadros_total = cuadros_conv + round(PAUSA_FINAL * FPS)
    FASE_PUNTO = 0.45  # fracción de cada iteración dedicada a marcar c; el resto, a encoger el intervalo

    def camara(s, a, b):
        """Ventana del zoom: se encoge a ritmo exponencial constante (÷2 por iteración)."""
        media = 0.95 * ancho0 * 2.0 ** (-s)
        centro = (a + b) / 2
        return centro - media, centro + media

    def dibujar(i):
        s = min(i / cuadros_conv * n, n)
        k = min(int(s), n - 1)
        p = s - k if s < n else 1.0
        paso = pasos[k]
        terminado = s >= n

        if p < FASE_PUNTO and not terminado:
            u = suavizar(p / FASE_PUNTO)
            a, b = paso["a"], paso["b"]
            alto_tallo, alpha_c, alpha_desc = u, u, 0.0
            lado_desc = None
        else:
            v = suavizar((p - FASE_PUNTO) / (1 - FASE_PUNTO)) if not terminado else 1.0
            a = paso["a"] + (paso["a2"] - paso["a"]) * v
            b = paso["b"] + (paso["b2"] - paso["b"]) * v
            alto_tallo, alpha_c = 1.0, 1.0
            alpha_desc = 0.28 * math.sin(math.pi * v)
            lado_desc = paso["descarta"]

        c, fc = paso["c"], paso["fc"]
        fa, fb = f(a), f(b)

        for e in elementos:
            e["intervalo"].set_x(a)
            e["intervalo"].set_width(b - a)
            if lado_desc == "izq":
                e["descarte"].set_x(paso["a"])
                e["descarte"].set_width(c - paso["a"])
            elif lado_desc == "der":
                e["descarte"].set_x(c)
                e["descarte"].set_width(paso["b"] - c)
            e["descarte"].set_alpha(alpha_desc)
            e["linea_a"].set_xdata([a, a])
            e["linea_b"].set_xdata([b, b])
            e["pa"].set_data([a], [fa])
            e["pb"].set_data([b], [fb])
            visible_c = not terminado
            e["tallo"].set_data([c, c], [0, fc * alto_tallo]) if visible_c else e["tallo"].set_data([], [])
            e["pc"].set_data([c], [fc * alto_tallo]) if visible_c else e["pc"].set_data([], [])
            e["pc"].set_alpha(alpha_c)
            e["raiz"].set_data(([raiz], [0]) if terminado else ([], []))

        # Cámara del zoom
        x0, x1 = camara(s, a, b)
        xs = np.linspace(x0, x1, 500)
        ys = f(xs)
        for capa in curva_z:
            capa.set_data(xs, ys)
        ax_z.set_xlim(x0, x1)
        visibles = ys[np.isfinite(ys)]
        lo = min(visibles.min(), 0) if visibles.size else -1
        hi = max(visibles.max(), 0) if visibles.size else 1
        pad = 0.15 * (hi - lo or 1)
        ax_z.set_ylim(lo - pad, hi + pad)

        # Convergencia: aparece cada punto cuando empieza su iteración
        hasta = k + 1 if (p > 0 or terminado) else k
        linea_err.set_data(ks[:hasta], err[:hasta])
        linea_res.set_data(ks[:hasta], res[:hasta])

        # Panel de texto
        if terminado:
            info.set_text(f"✔ convergió en {n} iteraciones\n"
                          f"raíz  ≈ {raiz:.{decimales}f}\n"
                          f"f(raíz) = {pasos[-1]['fc']: .3e}\n"
                          f"error ≤ {err[-1]:.3e}")
            info.get_bbox_patch().set_edgecolor(COLOR["raiz"])
        else:
            info.set_text(f"iteración {paso['k']:>3} / {n}\n"
                          f"a    = {a: .{decimales}f}\n"
                          f"b    = {b: .{decimales}f}\n"
                          f"c    = {c: .{decimales}f}\n"
                          f"f(c) = {fc: .3e}\n"
                          f"|b − a| / 2 = {(b - a) / 2:.3e}")
            info.get_bbox_patch().set_edgecolor(COLOR["rejilla"])
        return []

    animacion = FuncAnimation(fig, dibujar, frames=cuadros_total, interval=1000 / FPS,
                              blit=False, repeat=False)

    if GUARDAR_COMO:
        escritor = "pillow" if GUARDAR_COMO.lower().endswith(".gif") else "ffmpeg"
        animacion.save(GUARDAR_COMO, writer=escritor, fps=FPS, dpi=100,
                       progress_callback=lambda i, t: print(f"\rGuardando {i + 1}/{t}", end=""))
        print(f"\nGuardado en {GUARDAR_COMO}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
