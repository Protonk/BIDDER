# Gap Weather

The same ACM survivor window is passed through three ambient numerical
semigroups: `⟨2,3⟩`, `⟨3,5⟩`, and `⟨5,7⟩`. For each `S`, keep only
the shared survivors `C_SurvA`: integers that survive the ACM bundle
and are also multiplicative atoms of `(S, ·)`.

Each ring, from center outward in that order, is the signed discrepancy
residual

    F_L(t) - t

of the shifted decimal-tail orbit of that `C_SurvA` digit stream. Warm
area means the orbit has accumulated too much mass below `t`; cool area
means too little. The radial height is the shape behind the
single number `D_L*`.

The gaps of `S` are not drawn directly. They are the pressure system
that bends the survivor stream.

## Files

- `gap_weather.py` — renderer.
- `gap_weather.png` — image.
- `gap_weather.txt` — numeric readout for the semigroup path.
