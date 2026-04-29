# Boundary Loom

`boundary_loom.py` turns the boundary stitch diagnostic into one aligned
fabric. Each horizontal band is one monoid. Inside a band, downward motion
is boundary index. Across the band, columns are bit positions around the
entry join.

The central yellow thread is the join column: the leading `1` of the
incoming entry. The blue side is the trailing-bit side of the outgoing
entry. The orange side is the leading-bit side of the incoming entry.
Rows are compressed by averaging neighboring boundaries, so noise becomes
texture and bit-length drift becomes cloth.

Monoids are grouped by `v_2(n)`. The thin colored selvedge at both edges
marks that depth group. Within each group, odd parts increase downward.
This makes the forced-zero barcode visible as widening dark blue bands
immediately left of the join.

Red threads mark bins containing bit-length transitions. They are part of
the boundary object, not annotation.

`bent_loom.py` uses the same fabric, but maps it into a Poincare-disk
strip. The long direction becomes distance along a central geodesic, and
the width becomes perpendicular hyperbolic distance. The visible effect is
negative curvature: the loom opens in the middle and collapses toward the
ideal endpoints.
