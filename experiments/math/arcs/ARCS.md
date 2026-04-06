# Epsilon Landscape (Arcs)

The secant error epsilon_b(m) = log_b(1+m) - secant(m) plotted as a 3D
surface over (mantissa, base) space. Each base contributes one
cross-section — a concave bump whose height and peak position depend on
the base.

Run: `sage -python epsilon_landscape.py`

## Why it's art

The surface is a ruled shell, like a mathematical sculpture. For base 2
the bump is tall and broad (the familiar floating-point epsilon). As the
base increases, the bump flattens and its peak migrates toward m = 0.5.
The envelope of peaks traces a curve that connects the floating-point
world (base 2) to the Champernowne world (base 10) to arbitrary
positional systems.

## What makes it non-obvious

This bump is the error of approximating a logarithm by a straight line.
In base 2, the bump is `{(2⋆⁼1+𝕩)-𝕩}` — the exact SlideRule function
(see `experiments/binary/BINARY.md`, section 5). In base 10, the
sawtooth curve is `{10⋆⁼1+𝕩}` on m ∈ [0.1, 1].

It peaks where numbers have the richest factorization structure. The
landscape is a map of compositeness pressure across all bases — a bridge
between the ACM project and the SlideRule epsilon function.

## Format

Square (14" x 10"), dark background, viridis wire colormap. The viewing
angle (25 degrees elevation, -60 degrees azimuth) reveals both the bump shape
and the base-dependence.
