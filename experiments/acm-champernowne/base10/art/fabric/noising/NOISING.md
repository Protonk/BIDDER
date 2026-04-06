# Noising

These are destruction experiments on the fabric object.

Start with the rectangular digit field from
[`../digit_fabric.py`](../digit_fabric.py): rows are monoids, columns
are digit positions, and the visible geometry comes from digit-length
boundaries and sieve structure. Then ask a practical question:

What kind of damage actually breaks the fabric, and what kind only
changes its appearance?

The answer is sharper than it first looks.

## What is being tested

The noising branch compares three different kinds of attack:

- linear smoothing
- value relabeling
- a nonlinear attack inserted between two smoothing steps

The point is not image processing for its own sake. The point is to
learn which part of the fabric is carrying the structure:

- the exact pixel values
- the color labels attached to those values
- or the spatial arrangement of the digit-class boundaries

## `noising_gaussian.py`

[`noising_gaussian.py`](noising_gaussian.py) applies Gaussian blur at
increasing scales.

The result is that the fabric survives far longer than expected.

- `sigma = 2`: fine pixel grain softens, but the arcs remain
- `sigma = 8`: smaller arcs dissolve, broad sweeps remain
- `sigma = 32`: only large bands survive
- `sigma = 128`: nearly everything collapses into one soft gradient

This says the fabric is multiscale. The important curves are not a
single fragile edge set; they recur across scales because the same
digit-length mechanism keeps reappearing. Blur removes the fine copies
first, but the coarse copies keep the image legible.

## `noising_permutation.py`

[`noising_permutation.py`](noising_permutation.py) applies random digit
permutations.

This does essentially no structural damage.

The colors change. The geometry does not.

That matters because it tells us the fabric is not primarily chromatic.
Its order lives in the placement of regions, seams, and boundaries, not
in which literal digit has which color. A permutation is just a relabel.
It repaints the threads without moving the weave.

## `noising_sandwich.py`

[`noising_sandwich.py`](noising_sandwich.py) is the real attack:

1. blur a little
2. scramble values nonlinearly
3. blur a little again

This is more destructive than a single larger blur with the same rough
budget.

Why it works:

- the first blur turns discrete digits into continuous values
- the nonlinear scramble bends those values in a way a plain permutation
  cannot
- the second blur smooths the damage into the geometry itself

So the weak point is not "blur" alone. It is blur plus nonlinearity.
The first blur creates vulnerability. The scramble exploits it. The
second blur makes the damage spatially coherent.

## What survives and what breaks

Taken together, the branch says:

- pure blur weakens the fabric gradually
- pure relabeling does not weaken it at all
- nonlinear value distortion, once the field has been made continuous,
  can break it quickly

That is the core result of the branch. The fabric is resilient as a
geometric object, but not invulnerable. To really damage it, you have to
attack geometry through the value field rather than just smearing or
recoloring.

## Reading order

Read these in order:

1. `noising_gaussian.png`
2. `noising_permutation.png`
3. `noising_sandwich.png`

That order moves from "surprisingly ineffective" to "actually
destructive."
