<!--
  Profile README for @BladedGoose13
  Generated assets live in assets/ and are rebuilt by .github/workflows/.
  Palette and layout notes: scripts/palette.py
-->

<div align="center">

<img src="assets/hero.svg" alt="Maximilien Tragarz Quintana — computational physics, scientific computing, quantitative research" width="100%">

<br><br>

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=19&pause=900&duration=3400&color=E8DFD1&center=true&vCenter=true&width=860&height=46&lines=Computational+physics%2C+shipped+as+software.;DFT+%2B+HPC+%2B+SciML+in+reproducible+pipelines.;Math+that+has+to+survive+contact+with+real+data.;I+build+systems+that+run+themselves." alt="Computational physics, shipped as software.">

<p>
  <img src="https://img.shields.io/badge/Monterrey,_MX-2E4A47?style=for-the-badge&logo=googlemaps&logoColor=E8DFD1" alt="Monterrey, Mexico">
  <img src="https://img.shields.io/badge/Engineering_Physics_B.S.-4A3527?style=for-the-badge&logo=academia&logoColor=E8DFD1" alt="Engineering Physics B.S.">
  <img src="https://img.shields.io/badge/Heading_for-deep_tech_R%26D-6B4E3A?style=for-the-badge&logoColor=E8DFD1" alt="Heading for deep tech R&D">
  <img src="https://komarev.com/ghpvc/?username=BladedGoose13&style=for-the-badge&color=3A4E4C&label=VISITORS" alt="Profile visitors">
</p>

</div>

---

## `01` · Thesis

> **I like problems where the math has to survive contact with real data.**

I work at the intersection of **computational physics**, **scientific computing / SciML**, and
**data-driven industries** — density functional theory on one side, pipelines and autonomous
systems on the other. The part I actually enjoy is the seam between them: taking something that
only exists as a derivation and making it run, repeatedly, on hardware, without me babysitting it.

Long term I want to be doing research inside deep tech or R&D — somewhere **computation is the
product rather than the paperwork**.

<br>

<div align="center">
  <table>
    <tr>
      <td align="center" width="25%"><sub><b>I OPTIMISE FOR</b></sub><br>reproducibility</td>
      <td align="center" width="25%"><sub><b>NO PATIENCE FOR</b></sub><br>results you can't rerun</td>
      <td align="center" width="25%"><sub><b>SPECIALTY</b></sub><br>autonomous pipelines</td>
      <td align="center" width="25%"><sub><b>CURRENTLY</b></sub><br>DFT · SciML surrogates</td>
    </tr>
  </table>
</div>

---

## `02` · Telemetry

<div align="center">

<img src="assets/dashboard.svg" alt="Systems dashboard: contributions, commits, repositories, source mass, longest streak, language distribution and a 52-week contribution field" width="100%">

<br><br>

<img src="https://streak-stats.demolab.com?user=BladedGoose13&background=14201F&border=263835&stroke=263835&ring=D8A657&fire=D8A657&currStreakNum=E8DFD1&sideNums=C9B99A&currStreakLabel=D8A657&sideLabels=7E908C&dates=7E908C&border_radius=12" alt="Contribution streak" width="62%">

<br><br>

<img src="assets/snake.svg" alt="Contribution grid rendered as a snake animation" width="100%">

<sub>The dashboard above is generated from the GitHub GraphQL API and committed by
<a href=".github/workflows/dashboard.yml">a scheduled workflow</a> — not fetched from a
third-party card service, so it can't rate-limit, expire or 402.</sub>

</div>

---

## `03` · Architecture

Most of my work ends up looking like the same machine: data in, physics in the middle, a model
that decides what to compute next, and artefacts a human can actually read at the end.

<div align="center">

<img src="assets/pipeline.svg" alt="Autonomous research pipeline: ingest, validate, simulate, reduce, learn, serve, with an active-learning feedback loop" width="100%">

</div>

<details>
<summary><b>The same loop, as a graph</b></summary>

<br>

```mermaid
%%{init: {'theme':'base','themeVariables':{
  'primaryColor':'#1B2A28','primaryTextColor':'#E8DFD1','primaryBorderColor':'#3A4E4C',
  'lineColor':'#6B4E3A','secondaryColor':'#2E4A47','tertiaryColor':'#14201F',
  'fontFamily':'ui-monospace, SFMono-Regular, monospace','fontSize':'13px'}}}%%
flowchart LR
    subgraph SRC[" sources "]
        A1[instrument data]
        A2[public datasets]
        A3[prior simulations]
    end

    subgraph CORE[" compute "]
        B[validate<br/>schema · units · bounds]
        C[simulate<br/>Quantum ESPRESSO · Slurm]
        D[reduce<br/>descriptors · tensors]
        E[learn<br/>SciML surrogate + UQ]
    end

    subgraph OUT[" artefacts "]
        F[API / dashboard]
        G[figures · LaTeX]
    end

    A1 & A2 & A3 --> B --> C --> D --> E
    E --> F
    E --> G
    E -. "acquisition function<br/>picks the next run" .-> C

    classDef s fill:#14201F,stroke:#263835,color:#C9B99A
    classDef c fill:#1B2A28,stroke:#3A4E4C,color:#E8DFD1
    classDef o fill:#2E4A47,stroke:#4B6B60,color:#E8DFD1
    class A1,A2,A3 s
    class B,C,D,E c
    class F,G o
```

**Non-negotiables.** Every stage is idempotent and restartable. Inputs are content-addressed, so a
figure can always be traced back to the exact run that produced it. Nothing important happens on
my laptop — if it can't run in a container on a scheduler, it isn't finished.

</details>

---

## `04` · Instruments

<table>
<tr><td width="150"><sub><b>LANGUAGES</b></sub></td><td>
  <img src="https://img.shields.io/badge/Python-2E4A47?style=for-the-badge&logo=python&logoColor=E8DFD1" alt="Python">
  <img src="https://img.shields.io/badge/C%2B%2B-4A3527?style=for-the-badge&logo=cplusplus&logoColor=E8DFD1" alt="C++">
  <img src="https://img.shields.io/badge/MATLAB-6B4E3A?style=for-the-badge&logo=octave&logoColor=E8DFD1" alt="MATLAB">
  <img src="https://img.shields.io/badge/Bash-3A4E4C?style=for-the-badge&logo=gnubash&logoColor=E8DFD1" alt="Bash">
  <img src="https://img.shields.io/badge/SQLite-2E4A47?style=for-the-badge&logo=sqlite&logoColor=E8DFD1" alt="SQLite">
  <img src="https://img.shields.io/badge/LaTeX-4A3527?style=for-the-badge&logo=latex&logoColor=E8DFD1" alt="LaTeX">
</td></tr>

<tr><td><sub><b>SCIENTIFIC PYTHON</b></sub></td><td>
  <img src="https://img.shields.io/badge/NumPy-6B4E3A?style=for-the-badge&logo=numpy&logoColor=E8DFD1" alt="NumPy">
  <img src="https://img.shields.io/badge/SciPy-3A4E4C?style=for-the-badge&logo=scipy&logoColor=E8DFD1" alt="SciPy">
  <img src="https://img.shields.io/badge/pandas-2E4A47?style=for-the-badge&logo=pandas&logoColor=E8DFD1" alt="pandas">
  <img src="https://img.shields.io/badge/Matplotlib-4A3527?style=for-the-badge&logo=chartdotjs&logoColor=E8DFD1" alt="Matplotlib">
  <img src="https://img.shields.io/badge/Jupyter-3A4E4C?style=for-the-badge&logo=jupyter&logoColor=E8DFD1" alt="Jupyter">
  <img src="https://img.shields.io/badge/Anaconda-2E4A47?style=for-the-badge&logo=anaconda&logoColor=E8DFD1" alt="Anaconda">
</td></tr>

<tr><td><sub><b>MACHINE LEARNING</b></sub></td><td>
  <img src="https://img.shields.io/badge/PyTorch-4A3527?style=for-the-badge&logo=pytorch&logoColor=E8DFD1" alt="PyTorch">
  <img src="https://img.shields.io/badge/scikit--learn-6B4E3A?style=for-the-badge&logo=scikitlearn&logoColor=E8DFD1" alt="scikit-learn">
  <img src="https://img.shields.io/badge/Scientific_ML-3A4E4C?style=for-the-badge&logo=tensorflow&logoColor=E8DFD1" alt="Scientific ML">
</td></tr>

<tr><td><sub><b>PHYSICS &amp; HPC</b></sub></td><td>
  <img src="https://img.shields.io/badge/Quantum_ESPRESSO-4A3527?style=for-the-badge&logo=qiskit&logoColor=E8DFD1" alt="Quantum ESPRESSO">
  <img src="https://img.shields.io/badge/DFT_%26_SOC-6B4E3A?style=for-the-badge&logo=moleculer&logoColor=E8DFD1" alt="DFT and spin-orbit coupling">
  <img src="https://img.shields.io/badge/Linux-3A4E4C?style=for-the-badge&logo=linux&logoColor=E8DFD1" alt="Linux">
  <img src="https://img.shields.io/badge/Slurm_%26_HPC-2E4A47?style=for-the-badge&logo=linuxfoundation&logoColor=E8DFD1" alt="Slurm and HPC">
  <img src="https://img.shields.io/badge/CUDA-4A3527?style=for-the-badge&logo=nvidia&logoColor=E8DFD1" alt="CUDA">
</td></tr>

<tr><td><sub><b>BUILD &amp; SHIP</b></sub></td><td>
  <img src="https://img.shields.io/badge/Git-6B4E3A?style=for-the-badge&logo=git&logoColor=E8DFD1" alt="Git">
  <img src="https://img.shields.io/badge/Docker-2E4A47?style=for-the-badge&logo=docker&logoColor=E8DFD1" alt="Docker">
  <img src="https://img.shields.io/badge/FastAPI-4A3527?style=for-the-badge&logo=fastapi&logoColor=E8DFD1" alt="FastAPI">
  <img src="https://img.shields.io/badge/Streamlit-6B4E3A?style=for-the-badge&logo=streamlit&logoColor=E8DFD1" alt="Streamlit">
  <img src="https://img.shields.io/badge/Overleaf-2E4A47?style=for-the-badge&logo=overleaf&logoColor=E8DFD1" alt="Overleaf">
</td></tr>

<tr><td><sub><b>HARDWARE</b></sub></td><td>
  <img src="https://img.shields.io/badge/KiCad-4A3527?style=for-the-badge&logo=kicad&logoColor=E8DFD1" alt="KiCad">
  <img src="https://img.shields.io/badge/ESP32-6B4E3A?style=for-the-badge&logo=espressif&logoColor=E8DFD1" alt="ESP32">
  <img src="https://img.shields.io/badge/Arduino-3A4E4C?style=for-the-badge&logo=arduino&logoColor=E8DFD1" alt="Arduino">
</td></tr>
</table>

---

## `05` · Selected work

<table>
<tr>
<td width="50%" valign="top">

### [QE-Workflow](https://github.com/BladedGoose13/QE-Workflow)
`Quantum ESPRESSO` `DFT` `Gnuplot`

Electronic structure of **silicon-doped graphene**. Undergraduate research training in
computational materials science at Tec de Monterrey, under Dr. José Ángel Reyes Retana.

Two stages: reproduce the known graphene band structure to validate the setup, then extend to an
original study of Si doping through the **Virtual Crystal Approximation**. Presented as a poster
at the **Tec Science Summit 2026** (NextGen Scientists Program).

</td>
<td width="50%" valign="top">

### [ThermoHub.Sim](https://github.com/BladedGoose13/ThermoHub.Sim---V1.0)
`Python` `Streamlit` `thermodynamics`

Simulation software for thermodynamic processes in industrial systems. Reads and **interpolates
steam tables** — saturation by *T* and *P*, superheated and compressed regions — and exposes the
whole thing through a Streamlit UI so a non-programmer can drive it.

</td>
</tr>
<tr>
<td width="50%" valign="top">

### [LUMIO — ESG Framework](https://github.com/BladedGoose13/ESG-Framework-LUMIO)
`Monte Carlo` `optimisation` `decision analysis`

Quantitative ESG and impact-analytics framework for evaluating, comparing and prioritising
initiatives. Built for **Consult for a Cause 2026** (Tec Consulting Club, with Xignux and
Strategy& — PwC Network).

</td>
<td width="50%" valign="top">

### [PathWise](https://github.com/BladedGoose13/PathWise)
`Python` `Docker` `LLM` `EdTech`

> *"The integrated EdTech ecosystem that converts scattered potential into structured success."*

An end-to-end platform rather than a script — and the project where I learned most of what I know
about shipping something other people have to use.

</td>
</tr>
</table>

<div align="center"><sub>
  Also around: <a href="https://github.com/BladedGoose13/STREAMLIT-Memorama">STREAMLIT-Memorama</a>
  — a pattern-recognition memory game, because not everything needs a Hamiltonian.
</sub></div>

---

## `06` · The math it rests on

The day job, compressed. Self-consistent Kohn–Sham, which is what Quantum ESPRESSO is actually
solving on every SCF cycle:

```math
\left[-\frac{\hbar^{2}}{2m}\nabla^{2} + v_{\text{eff}}[\rho](\mathbf{r})\right]\psi_{i}(\mathbf{r})
= \varepsilon_{i}\,\psi_{i}(\mathbf{r}),
\qquad
\rho(\mathbf{r}) = \sum_{i}^{N} \left|\psi_{i}(\mathbf{r})\right|^{2}
```

Doping a lattice without building a supercell for every concentration — the Virtual Crystal
Approximation, a weighted blend of pseudopotentials:

```math
V_{\text{VCA}}^{\,\text{ps}} = (1-x)\,V_{\text{C}}^{\,\text{ps}} + x\,V_{\text{Si}}^{\,\text{ps}}
```

And the part that makes it a pipeline instead of a pile of runs — a surrogate penalised for
disagreeing with the physics, not just with the data:

```math
\mathcal{L}(\theta) = \underbrace{\frac{1}{N}\sum_{n}\left\|u_{\theta}(t_{n}) - u_{n}\right\|^{2}}_{\text{data}}
\; + \; \lambda \underbrace{\left\|\frac{\mathrm{d}u_{\theta}}{\mathrm{d}t} - f(u_{\theta},t)\right\|^{2}}_{\text{residual}}
```

<sub>The banner at the top is not decoration either: it's a superposition of point vortices in a
uniform stream, <code>w(z) = U + Σ Γₖ/2πi(z − zₖ)</code>, integrated with RK4 at <code>h = 0.016</code>.
Those are real integral curves. Source: <a href="scripts/gen_hero.py">scripts/gen_hero.py</a>.</sub>

---

## `07` · Off duty

Indie and chill rock on repeat. The gym — **not your average joe, I promise**. Anime, a healthy
amount of videogames, and crafts when I need my hands busy instead of my head.

Coffee and bakery enjoyer, and I'd argue **connoisseur**. I also love travelling and meeting new
people, which is the fastest way I know to find out how little I know.

<p align="center">
  <img src="https://img.shields.io/badge/Valorant-6B4E3A?style=for-the-badge&logo=valorant&logoColor=E8DFD1" alt="Valorant">
  <img src="https://img.shields.io/badge/League_of_Legends-3A4E4C?style=for-the-badge&logo=leagueoflegends&logoColor=E8DFD1" alt="League of Legends">
  <img src="https://img.shields.io/badge/Spotify-2E4A47?style=for-the-badge&logo=spotify&logoColor=E8DFD1" alt="Spotify">
  <img src="https://img.shields.io/badge/COFFEE-6F4E37?style=for-the-badge&logo=buymeacoffee&logoColor=E8DFD1" alt="Coffee">
  <img src="https://img.shields.io/badge/Crunchyroll-6B4E3A?style=for-the-badge&logo=crunchyroll&logoColor=E8DFD1" alt="Crunchyroll">
  <img src="https://img.shields.io/badge/Lifting-3A4E4C?style=for-the-badge&logo=strava&logoColor=E8DFD1" alt="Lifting">
</p>

---

<div align="center">

### Talk to me

about physics, an album you can't stop replaying, or the best café in a city you think I
should visit.

<p>
  <a href="mailto:BladedGoose@gmail.com"><img src="https://img.shields.io/badge/Email-2E4A47?style=for-the-badge&logo=gmail&logoColor=E8DFD1" alt="Email"></a>
  <a href="https://github.com/BladedGoose13"><img src="https://img.shields.io/badge/GitHub-4A3527?style=for-the-badge&logo=github&logoColor=E8DFD1" alt="GitHub"></a>
</p>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0E1716,45:2E4A47,100:6B4E3A&height=130&section=footer" alt="" width="100%">

</div>
