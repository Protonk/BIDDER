# Walsh Upgrade Results

Robust universal cells after the Stage 0 bar: 23

## Robust Set

| cell | popcount | geometry | sequency | mean P[s] | ratio | corr with v2 | monoids above baseline |
|---|---:|---|---:|---:|---:|---:|---:|
| 93 | 5 | mixed | 211 | 0.004653 | 1.191x | -0.152 | 26 |
| 103 | 5 | mixed | 187 | 0.004627 | 1.184x | -0.212 | 28 |
| 127 | 7 | contiguous | 171 | 0.004307 | 1.103x | -0.223 | 27 |
| 150 | 4 | mixed | 78 | 0.004220 | 1.080x | 0.238 | 25 |
| 155 | 5 | edge-loaded | 145 | 0.004544 | 1.163x | -0.134 | 26 |
| 158 | 5 | mixed | 81 | 0.004304 | 1.102x | 0.282 | 26 |
| 172 | 4 | mixed | 38 | 0.004517 | 1.156x | 0.515 | 25 |
| 174 | 5 | mixed | 89 | 0.004556 | 1.166x | -0.038 | 25 |
| 178 | 4 | mixed | 118 | 0.004541 | 1.162x | -0.072 | 28 |
| 179 | 5 | edge-loaded | 137 | 0.004585 | 1.174x | -0.052 | 29 |
| 180 | 4 | mixed | 54 | 0.004969 | 1.272x | 0.377 | 31 |
| 211 | 5 | edge-loaded | 141 | 0.004589 | 1.175x | -0.104 | 26 |
| 213 | 5 | edge-loaded | 205 | 0.004736 | 1.212x | -0.168 | 29 |
| 214 | 5 | mixed | 77 | 0.004483 | 1.148x | -0.157 | 25 |
| 215 | 6 | edge-loaded | 178 | 0.004673 | 1.196x | -0.141 | 28 |
| 218 | 5 | mixed | 109 | 0.004446 | 1.138x | 0.122 | 25 |
| 223 | 7 | edge-loaded | 173 | 0.004406 | 1.128x | -0.156 | 26 |
| 234 | 5 | mixed | 101 | 0.004628 | 1.185x | 0.110 | 26 |
| 235 | 6 | edge-loaded | 154 | 0.004453 | 1.140x | -0.136 | 26 |
| 246 | 6 | mixed | 74 | 0.004875 | 1.248x | 0.229 | 31 |
| 247 | 7 | edge-loaded | 181 | 0.004308 | 1.103x | -0.243 | 28 |
| 251 | 7 | edge-loaded | 149 | 0.004430 | 1.134x | -0.166 | 25 |
| 255 | 8 | full | 170 | 0.005447 | 1.394x | -0.095 | 31 |

## Stage 1

- Survive phase-averaging across 32 sampled offsets: 93, 103, 150, 155, 158, 172, 174, 178, 179, 180, 211, 213, 214, 215, 223, 234, 235, 246, 247, 251, 255
- Chunk-size persistence: 127 -> k=6@63, k=7@127; 172 -> k=6@54; 213 -> k=7@109; 215 -> k=6@63; 218 -> k=9@426; 223 -> k=6@63, k=7@127; 235 -> k=6@63, k=7@123; 246 -> k=6@63; 247 -> k=6@63, k=7@127; 251 -> k=6@63, k=7@127; 255 -> k=6@63, k=7@127
- Boundary concentration classes:
  - 93 -> 2+ only (degenerate)
  - 103 -> 2+ only (degenerate)
  - 127 -> 2+ only (degenerate)
  - 150 -> 2+ only (degenerate)
  - 155 -> 2+ only (degenerate)
  - 158 -> 2+ only (degenerate)
  - 172 -> 2+ only (degenerate)
  - 174 -> 2+ only (degenerate)
  - 178 -> 2+ only (degenerate)
  - 179 -> 2+ only (degenerate)
  - 180 -> 2+ only (degenerate)
  - 211 -> 2+ only (degenerate)
  - 213 -> 2+ only (degenerate)
  - 214 -> 2+ only (degenerate)
  - 215 -> 2+ only (degenerate)
  - 218 -> 2+ only (degenerate)
  - 223 -> 2+ only (degenerate)
  - 234 -> 2+ only (degenerate)
  - 235 -> 2+ only (degenerate)
  - 246 -> 2+ only (degenerate)
  - 247 -> 2+ only (degenerate)
  - 251 -> 2+ only (degenerate)
  - 255 -> 2+ only (degenerate)

At `k=8`, the boundary-conditioned split is not a real separator: every 256-bit chunk in the run already contains multiple entry boundaries.
So this stage only tells us the survivors live on boundary-rich windows at that scale; it does not separate boundary effects from interior effects.

## Stage 2

| cell | length-matched | v2-preserving | entry-order shuffle | fair-coin calibration mean |
|---|---|---|---|---:|
| 93 | yes | no | no | 0.003908 |
| 103 | no | no | no | 0.003921 |
| 127 | no | no | no | 0.003906 |
| 150 | no | no | no | 0.003899 |
| 155 | no | no | no | 0.003924 |
| 158 | no | no | no | 0.003922 |
| 172 | no | no | no | 0.003887 |
| 174 | no | no | no | 0.003911 |
| 178 | no | no | no | 0.003902 |
| 179 | yes | no | no | 0.003906 |
| 180 | yes | no | no | 0.003919 |
| 211 | yes | no | no | 0.003882 |
| 213 | yes | no | no | 0.003893 |
| 214 | no | no | no | 0.003911 |
| 215 | no | no | no | 0.003917 |
| 218 | no | no | no | 0.003890 |
| 223 | no | no | no | 0.003906 |
| 234 | yes | no | no | 0.003897 |
| 235 | no | no | no | 0.003914 |
| 246 | yes | no | no | 0.003907 |
| 247 | no | no | no | 0.003921 |
| 251 | yes | no | no | 0.003900 |
| 255 | yes | yes | no | 0.003914 |
