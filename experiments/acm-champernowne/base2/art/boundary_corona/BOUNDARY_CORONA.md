# Boundary Corona

`boundary_corona.py` is the polar version of the diagnostic stitch view
from `../../forest/boundary_stitch/`. It uses the same local object: a
fixed-width window of bits around every entry boundary in the binary
ACM-Champernowne stream.

The coordinate change is simple. Boundary index becomes angle. Bit
position relative to the join becomes radius. The join column, which is
the leading `1` of the incoming entry, becomes the bright yellow ring.
Trailing bits of the outgoing entry sit inside that ring. Leading bits
of the incoming entry sit outside it.

That makes the `v_2(n)` barcode physical. For odd `n`, there is no
guaranteed dark band inside the join. For powers of two, each extra
factor of two adds one more forced-zero annulus just inside the ring.
Mixed even monoids, such as `6` and `12`, show the same dark barcode
width as their `v_2` peer but keep different surrounding texture.

The orange exterior is the right side of the boundary stitch. It is not
just decoration: it is the leading-bit side of the incoming entries, so
smooth sectors appear when consecutive n-primes move through a bit-length
class. The blue interior, outside the forced-zero block, is the noisy
trailing-bit side.

Red radial glints mark bit-length transitions, where consecutive entries
cross a power-of-two threshold. They are rare for small monoids and more
visible when the entry scale changes quickly.

The result is an art view of the comma-character question. If the
boundary is self-synchronizing, the ring system should look rigid: a
bright join, a predictable dark interior barcode, and only controlled
contamination elsewhere. If interior structure competes with the boundary
syntax, the corona gets noisy in exactly the place the diagnostic cares
about.
