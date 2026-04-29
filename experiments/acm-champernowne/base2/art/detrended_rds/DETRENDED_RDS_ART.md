# Detrended RDS Art

This folder turns the disparity residuals into pure images.

`shuffle_funeral.py` uses the same setup as
`../../disparity/detrended_rds.py`: generate each monoid's binary
stream, subtract the per-entry closed-form RDS drift, and compare the
original entry order against a seeded shuffled-entry control.

The image is a diptych. The left half is original order; the right half
is shuffled order. Each vertical plume is one monoid. Residual amplitude
controls brightness and sideways displacement. Local slope controls curl.
Zero crossings cut dark horizontal scars through the plume.

The point is the contrast: the original residuals keep coherent slow
motion after detrending, while the shuffled controls lose most of that
gesture and settle into grey ash.

`shuffle_funeral_polar.py` wraps the same image into polar coordinates.
The rectangular x-axis becomes angle and the residual run moves outward
from the inner ring. The colored original-order plumes and grey shuffled
ash become separate arcs of the same circular wake.

`residual_tide.py` drops the shuffled control and renders only the
original per-entry residuals. Each monoid is normalized by its own maximum
excursion, stacked as a translucent ribbon, and colored by `v_2(n)`. The
image is about phase and slow order-dependent motion, not residual size.

`residual_tide_polar.py` wraps that tide field into an annulus. Bit
position becomes angle; the monoid stack becomes radius. The result keeps
the normalized residual motion but turns it into nested luminous rings.
