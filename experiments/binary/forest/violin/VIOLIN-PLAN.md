# Violin Plan

Three visualizations of the sawtooth, its concavity bump, and the
running mean — plotted together as interacting curves. The name
"violin" because the bump arches nested inside the sawtooth teeth
look like the f-holes of a string instrument, and because the
running mean is the bow drawing across them.


## 1. Diagnostic: The Three Curves, Honest

`violin_diagnostic.py`

A single tall panel, n = 1..4000. Three traces on the same axes,
no per-tooth secant subtraction, no normalization tricks:

- **Yellow:** C_2(n) itself (not its log). The raw sawtooth,
  sweeping [1.5, 2.0) per tooth, teeth at powers of 2.
- **Red:** The running mean M(n) = (1/n) * sum C_2(1..n). A smooth
  curve approaching 7/4 = 1.75 from below, with visible dips at
  each power of 2 as new low values (near 1.5) enter the average.
- **Blue:** The theoretical midline per tooth: (3 + m)/2 evaluated
  at the tooth's midpoint mantissa m = 0.5, giving 1.75. A
  horizontal reference at 7/4.

No secant subtraction. No bump extraction. Just the three objects
in their natural coordinates: the signal, its average, and the
target. The diagnostic value: see directly how wide the sawtooth
range is (0.5 units), how deep the running-mean dips are at each
boundary, and how the dips heal. The healing rate is the story —
in base 10 each tooth brings 10x fresh data, so dips close fast.
In base 2, each tooth brings only 2x, so dips linger. The plot
shows this as a visible asymmetry: the left edge of each
running-mean trough is steep (new low values arrive), the right
edge is gentle (recovery diluted by history).


## 2. Artistic: Binade Fans

`violin_fans.py`

One panel per binade (bit-length class), arranged as a horizontal
strip of squares. Within each square, draw both curves — the
sawtooth tooth and the running-mean trace for that binade — but
normalize both to [0, 1] on both axes (mantissa m on x, rescaled
value on y). This strips away the absolute scale and shows pure
shape.

The sawtooth tooth is always the same concave arch (the curve
log_2((3+m)/2), rescaled). The running-mean trace changes from
binade to binade: in early binades it swings wildly (the mean is
volatile); in late binades it barely moves (the mean is anchored
by thousands of prior values). The visual effect: a fan that
closes. The first few squares show two distinct curves (arch and
oscillation). The later squares show the arch alone — the
running-mean trace has flattened into a horizontal line,
indistinguishable from the midpoint. The "fan" is the shrinking
gap between the two curves as history accumulates.

Color each square's background by the binade's running-mean dip
depth (how far M(n) drops below 7/4 at the start of that binade).
Early binades: warm (deep dip). Late binades: cool (shallow dip).
The gradient across the strip is the convergence rate made visible.

Black background, white curves, warm-to-cool binade backgrounds.
The strip reads left to right like a film reel of the running mean
losing its individuality.


## 3. Derived: Binade Gini Coefficients

`violin_gini.py`

For each binade d, compute two scalars from the curves within
that binade:

**Area ratio.** The area between the sawtooth tooth and its secant
(the concavity excess), divided by the total area under the tooth
(above y = 0). This is a normalized measure of how "bowed" the
tooth is. For the theoretical curve g(m) = log_2((3+m)/2), the
ratio is constant across binades (~0.015/0.79 ≈ 0.019). For the
actual data, it absorbs the second-order staircase: the area
ratio should decrease slightly per binade as the later entries
linearize the curve.

**Running-mean Gini.** Treat the running-mean values within the
binade as a "population" and compute their Gini coefficient — the
normalized area between the Lorenz curve and the diagonal. A Gini
of 0 means the running mean is perfectly flat within the binade
(all values equal — full convergence). A Gini near its maximum
means the running mean varies widely (still volatile — far from
convergence). The Gini should decay across binades as the running
mean stabilizes.

Plot both scalars vs binade index d on the same axes. The area
ratio is roughly constant (a property of the function, not of
convergence). The Gini decays (a property of the averaging, not
of the function). The two curves cross at a specific binade d* —
the binade where the running mean becomes "flatter than the bump
is tall." Before d*: the mean's variation dominates the bump.
After d*: the bump dominates the mean's variation.

This crossing point d* is the binade where the running mean stops
carrying per-tooth structure and becomes purely a convergence
story. It's the answer to "when does the running mean forget which
tooth it's in?" — and it should depend on the base (in base 10,
d* is small because 10x growth kills per-tooth variation fast; in
base 2, d* is larger).
