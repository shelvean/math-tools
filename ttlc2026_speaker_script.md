# Browser-Native Mathematics: A Tool Collection
Speaker script · TTLC 2026 · Shelvean Kapita
Target runtime: ~8 min 30 sec · 15 slides · ~140 wpm

Reading key. [bracketed] = stage direction or click cue, do not read.

---

## SLIDE 1 — Title · ≈ 25 sec
running total: 0:25

Good morning. I'm Shelvean Kapita from the Math Department. Over the last sixteen months I've built a collection of about sixty interactive mathematics tools that run in any web browser — no installs, no logins, no licenses. Today I'll describe what's in the collection and how the tools are designed.

[click — slide 2]

---

## SLIDES 2–5 — Why the browser · ≈ 55 sec total
running total: 1:20

(Slide 2.) Most computational tools students reach for today — calculators, CAS, LLMs — return an answer. They don't return a process.

(Slide 3.) Differential equations and dynamical systems ask students to picture a process: how a damped pendulum decays, how a phase portrait fills in, how a bifurcation reorganizes trajectories. The textbook can't show that. A browser can.

(Slide 4.) That is the gap the collection addresses.

(Slide 5.) Everything I'll show is a static HTML file with JavaScript. No server, no account, no install. The link is the tool.

[click — slide 6]

---

## SLIDE 6 — Context for the collection · ≈ 30 sec
running total: 1:50

A bit of context before the tour. The collection has been online for sixteen months as open educational resources on GitHub Pages. Most users arrive through ordinary Google searches — someone looks up a topic, lands on the page, uses the tool. The reach is international, with steady traffic from a number of universities; the about page on the site has the geographic breakdown for anyone interested. The point I want to make from this slide is not the count, but that the format works: an HTML page found in a search result is enough.

[click]

---

## SLIDE 7 — Math 308: Differential Equations · ≈ 25 sec
running total: 2:15

My main course is Math 308, Differential Equations for engineers. The standard topic sequence — first-order equations, second-order linear systems, Laplace transforms, systems of ODEs, phase plane analysis — each topic has a corresponding tool, and the tools share a common design pattern that I'll spend the next few slides describing.

[click]

---

## SLIDE 8 — Oscillations: design walk-through · ≈ 65 sec
running total: 3:20

The mass-spring tool is a good way to introduce the design pattern, because every tool in the collection follows it.

There is a panel of sliders on the side — mass, damping, spring constant, forcing amplitude, forcing frequency. As any slider moves, the animation updates continuously: the spring stretches and contracts in real time, the displacement trace draws itself across a time axis, and a small phase-plane inset draws the trajectory in position-velocity coordinates. Three views, one slider, all live.

Above the sliders is a drop-down menu of examples. The menu lists the parameter combinations that have qualitative names — the cases the textbook gives separate sections to. For mass-spring the entries are:

- Underdamped — c² < 4mk
- Critically damped — c² = 4mk
- Overdamped — c² > 4mk
- Undamped resonance — forcing at the natural frequency
- Beats — forcing near, but not at, the natural frequency

Pick a preset and the sliders snap to the corresponding values; the animation plays the canonical behavior. Then nudge a slider and watch how the picture deforms off the special value. The preset menu is a catalog of named cases. The sliders are the off-catalog space between them. The animation is the connection.

The same tool extends to coupled masses — two masses produce visible beats, four masses produce three normal modes you can identify by eye.

[click]

---

## SLIDE 9 — Phase portraits · ≈ 40 sec
running total: 4:00

Same design pattern, applied to a 2×2 linear system. The matrix entries are sliders. The vector field redraws as the entries change. Click anywhere in the plane to drop an initial condition, and a trajectory animates outward — forward in time in one color, backward in another. The eigenvectors are drawn as rays whenever they're real.

The drop-down menu has every canonical case: stable node, unstable node, saddle, stable spiral, unstable spiral, center, degenerate node, and the borderline cases where the discriminant or trace crosses zero. The student steps through the catalog, watches each portrait animate from a clean state, and then perturbs the matrix entries to see how the picture deforms across each boundary.

[click]

---

## SLIDE 10 — Linear programming · ≈ 35 sec
running total: 4:35

This one is from Math 140, Business Math. The design is different in shape but the same in spirit. The student types in linear constraints. As each constraint is added, its half-plane shades in with a fade animation; the feasible region is the intersection that emerges. The corner points are computed and labeled, and the optimum vertex highlights with the objective value displayed beside it.

The drop-down menu has standard textbook problems — the diet problem, a transportation problem, a production-mix problem — so the student can load a known case, watch the geometry assemble, then edit the constraints and watch it reassemble.

[click]

---

## SLIDE 11 — Dynamical systems · ≈ 35 sec
running total: 5:10

The nonlinear tools — Duffing, Lorenz, Van der Pol, Rössler, Lotka-Volterra, the Malkus waterwheel, the elastic pendulum — apply the same design at higher complexity. Sliders for the parameters. A time-series animation, a phase-space animation, sometimes a third panel for a Poincaré section, all running off the same integrator step.

The drop-down menu is the entry point. For Duffing it includes the symmetric double well, the chaotic regime, and a period-doubling sequence. Picking a preset puts the system into that regime immediately, with the trajectory animating in real time so the qualitative behavior is visible inside a few seconds. Without the preset menu these tools are hard to use; parameter hunting is its own skill. With the menu, the student starts where the textbook starts, and explores from there.

[click — slide 12]

---

## SLIDE 12 — Why JavaScript · ≈ 60 sec
running total: 6:10

A note on the language. The criterion was: the student opens the link, the math runs. That ruled out most options.

Java applets are no longer supported in mainstream browsers. MATLAB and Maple require institutional licenses. A Python install requires Python, pip, a virtual environment, and a plotting library — four points where the student can fall off before seeing any math.

JavaScript runs in every browser on every device. The math in these tools is plain JavaScript — the integrators, the eigenvalue computations, the root finders. They are short, in the file, readable. There is no numerical library being called. A student who wants to see exactly which Runge-Kutta step the page is using can open the source.

The animation loop is the browser's `requestAnimationFrame` — same as a video game. That keeps the integration step synchronized with the screen refresh, which is why the trajectories animate smoothly even on a phone.

[click]

---

## SLIDE 13 — How the collection is maintained · ≈ 60 sec
running total: 7:10

A practical note on maintenance, because this is the part that has changed in the last year.

In 2025, each tool was edited by hand. Standardizing the navigation bar across the collection meant opening sixty files. Cross-cutting changes drifted easily.

In 2026, with agentic editing — Claude Code — a single prompt can edit every file in the collection. The agent reads the files, makes the edits, runs tests, and commits to GitHub.

The mathematical content, the choice of which equation to put on screen, which sliders to expose, which presets belong in the drop-down — that is the work, and it's mine. What changed is the file-by-file mechanics. A portfolio of this scale used to require a team to keep consistent. It now requires careful specifications and disciplined testing.

[click]

---

## SLIDE 14 — Accessibility · ≈ 35 sec
running total: 7:45

The tools target WCAG 2.1 AA across the collection. High-contrast palette, visible focus rings, full keyboard navigation on every slider and drop-down, and MathJax configured with the MathCAT pipeline so equations are read correctly by screen readers. This was a requirement of the Provost's Office OER grant supporting the work, not an addition after the fact.

[click — final slide]

---

## SLIDE 15 — What's next · ≈ 45 sec
running total: 8:30

Continuing work: more tutorial tools with Phil Yasskin in the department, the Math 308 question bank funded by the OER grant, and additional tools on request from instructors who reach out.

Gilbert Strang at MIT and Steven Strogatz at Cornell both replied when I sent them the link last summer; the replies are reproduced on the about page of the site.

The collection is at `shelvean.github.io/math-tools`.

Thank you.

[hold for Q&A]

---

## Pacing checkpoints
- Slide 6 should be brief — out by 1:55. If running long, cut the "point I want to make" sentence and move on.
- Slide 8 is the longest — keep it under 65 seconds.
- Slide 12 should start by 5:30. If later, drop the `requestAnimationFrame` aside.
- Slide 15 should start by 7:50.
