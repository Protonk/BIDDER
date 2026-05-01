Wobble (keep the existing term): the peak is off-center. Your worst error is concentrated in one part of the mantissa, not evenly distributed. This is the traditional wobble — the non-uniform grid spacing means precision is wasted unevenly. Base 2 has the most wobble (peak at m ≈ 0.75, way off midpoint). High bases have less (peak near 0.5).                                    

Wibble (new): the bump is asymmetric about its peak. Even once you've found the worst-case mantissa, the error landscape around it is skewed — it falls off steeply on one side and gently on the other. You can't
characterize the local error with a single "width" parameter. Base 10+ has more wibble (wide asymmetric  interval, strong curvature gradient). Base 2 has the least (narrow interval, nearly parabolic).

The reason to flip: traditional wobble already describes the non-uniformity of where precision is lost, which maps to off-center peaks. Wibble is the new observation — even after you center the peak, the shape of the error betrays you.                 

And the conservation law: every base pays a combined tax. You can center the peak (low wobble) but then the shape skews (high wibble). You can symmetrize the shape (low wibble) but the peak drifts off-center (high
wobble). The product wobble × wibble has a floor. No base gets both.
