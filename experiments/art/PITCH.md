# Art from Arithmetic Congruence Monoids

Five visualizations that make the algebraic structure of ACM-Champernowne
encoding visible. Each one renders a different aspect of the construction
— the sieve, the encoding, the error, the failure of addition — as an
image that works on its own terms, not just as a plot with a caption.

| Piece             | Location                  | Doc                          |
|-------------------|---------------------------|------------------------------|
| Rolling Shutter   | `experiments/shutter/`    | [SHUTTER.md](../shutter/SHUTTER.md) |
| Digit Fabric      | `experiments/art/fabric/` | [FABRIC.md](fabric/FABRIC.md)       |
| Moire Sieves      | `experiments/art/sieves/` | [SIEVES.md](sieves/SIEVES.md)       |
| Sieve Carpet      | `experiments/art/sieves/` | [SIEVES.md](sieves/SIEVES.md)       |
| Epsilon Landscape  | `experiments/math/arcs/`  | [ARCS.md](../math/arcs/ARCS.md)     |


## What didn't work

**Polar rosette.** The [1.1, 2.0] range is too narrow to produce visible
petals. Each digit class traces a nearly perfect circle with
imperceptible radial wobble. Scripts still in `experiments/art/`.

**Phase winding.** Same problem — the loops are nearly circular because
the sawtooth amplitude is small relative to the mean radius.

Both failures point to the same lesson: the sawtooth's *shape* is
interesting but its *amplitude* is not. The successful pieces encode
combinatorial structure (fabric, carpet) or statistical consequences
(shutter, moire), not the raw waveform.
