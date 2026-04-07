# Walsh Upgrade Results

Robust universal cells after the Stage 0 bar: 44

## Robust Set

| cell | popcount | geometry | sequency | mean P[s] | ratio | corr with v2 | monoids above baseline |
|---|---:|---|---:|---:|---:|---:|---:|
| 22 | 3 | low-bit-heavy | 79 | 0.004846 | 1.241x | 0.513 | 30 |
| 30 | 4 | contiguous | 80 | 0.004727 | 1.210x | 0.428 | 31 |
| 69 | 3 | mixed | 195 | 0.006175 | 1.581x | -0.071 | 31 |
| 71 | 4 | low-bit-heavy | 188 | 0.006212 | 1.590x | -0.034 | 31 |
| 73 | 3 | mixed | 227 | 0.004623 | 1.183x | -0.180 | 25 |
| 77 | 4 | mixed | 220 | 0.004975 | 1.274x | -0.118 | 26 |
| 93 | 5 | mixed | 211 | 0.004653 | 1.191x | -0.152 | 26 |
| 101 | 4 | mixed | 196 | 0.004650 | 1.190x | -0.154 | 28 |
| 103 | 5 | mixed | 187 | 0.004627 | 1.184x | -0.212 | 28 |
| 105 | 4 | mixed | 228 | 0.005118 | 1.310x | -0.058 | 26 |
| 119 | 6 | mixed | 180 | 0.004870 | 1.247x | -0.145 | 29 |
| 127 | 7 | contiguous | 171 | 0.004307 | 1.103x | -0.223 | 27 |
| 139 | 4 | edge-loaded | 158 | 0.005054 | 1.294x | -0.036 | 30 |
| 142 | 4 | mixed | 94 | 0.005107 | 1.307x | 0.054 | 25 |
| 143 | 5 | edge-loaded | 161 | 0.005015 | 1.284x | -0.107 | 31 |
| 150 | 4 | mixed | 78 | 0.004220 | 1.080x | 0.238 | 25 |
| 154 | 4 | mixed | 110 | 0.004344 | 1.112x | 0.044 | 26 |
| 155 | 5 | edge-loaded | 145 | 0.004544 | 1.163x | -0.134 | 26 |
| 158 | 5 | mixed | 81 | 0.004304 | 1.102x | 0.282 | 26 |
| 162 | 3 | mixed | 121 | 0.006121 | 1.567x | 0.043 | 31 |
| 163 | 4 | edge-loaded | 134 | 0.006091 | 1.559x | 0.033 | 31 |
| 172 | 4 | mixed | 38 | 0.004517 | 1.156x | 0.515 | 25 |
| 174 | 5 | mixed | 89 | 0.004556 | 1.166x | -0.038 | 25 |
| 178 | 4 | mixed | 118 | 0.004541 | 1.162x | -0.072 | 28 |
| 179 | 5 | edge-loaded | 137 | 0.004585 | 1.174x | -0.052 | 29 |
| 180 | 4 | mixed | 54 | 0.004969 | 1.272x | 0.377 | 31 |
| 182 | 5 | mixed | 73 | 0.005220 | 1.336x | 0.422 | 30 |
| 187 | 6 | edge-loaded | 150 | 0.004645 | 1.189x | -0.120 | 25 |
| 211 | 5 | edge-loaded | 141 | 0.004589 | 1.175x | -0.104 | 26 |
| 213 | 5 | edge-loaded | 205 | 0.004736 | 1.212x | -0.168 | 29 |
| 214 | 5 | mixed | 77 | 0.004483 | 1.148x | -0.157 | 25 |
| 215 | 6 | edge-loaded | 178 | 0.004673 | 1.196x | -0.141 | 28 |
| 218 | 5 | mixed | 109 | 0.004446 | 1.138x | 0.122 | 25 |
| 219 | 6 | edge-loaded | 146 | 0.005190 | 1.329x | -0.020 | 26 |
| 223 | 7 | edge-loaded | 173 | 0.004406 | 1.128x | -0.156 | 26 |
| 232 | 4 | high-bit-heavy | 26 | 0.005436 | 1.392x | 0.250 | 30 |
| 234 | 5 | mixed | 101 | 0.004628 | 1.185x | 0.110 | 26 |
| 235 | 6 | edge-loaded | 154 | 0.004453 | 1.140x | -0.136 | 26 |
| 244 | 5 | high-bit-heavy | 53 | 0.004933 | 1.263x | 0.449 | 30 |
| 246 | 6 | mixed | 74 | 0.004875 | 1.248x | 0.229 | 31 |
| 247 | 7 | edge-loaded | 181 | 0.004308 | 1.103x | -0.243 | 28 |
| 251 | 7 | edge-loaded | 149 | 0.004430 | 1.134x | -0.166 | 25 |
| 254 | 7 | contiguous | 85 | 0.004736 | 1.212x | 0.054 | 27 |
| 255 | 8 | full | 170 | 0.005447 | 1.394x | -0.095 | 31 |

## Stage 1

- Survive phase-averaging across 32 sampled offsets: 22, 30, 69, 71, 73, 93, 101, 103, 119, 139, 143, 150, 155, 158, 162, 163, 172, 174, 178, 179, 180, 182, 187, 211, 213, 214, 215, 223, 232, 234, 235, 244, 246, 247, 251, 254, 255
- Chunk-size persistence: 30 -> k=6@30, k=7@30; 73 -> k=7@41; 105 -> k=10@337; 119 -> k=6@63; 127 -> k=6@63, k=7@127; 172 -> k=6@54; 187 -> k=6@63, k=7@123; 213 -> k=7@109; 215 -> k=6@63; 218 -> k=9@426; 219 -> k=6@63, k=7@123, k=9@427; 223 -> k=6@63, k=7@127; 235 -> k=6@63, k=7@123; 246 -> k=6@63; 247 -> k=6@63, k=7@127; 251 -> k=6@63, k=7@127; 254 -> k=6@63, k=7@127; 255 -> k=6@63, k=7@127
- Boundary concentration classes:
  - 22 -> 2+ only (degenerate)
  - 30 -> 2+ only (degenerate)
  - 69 -> 2+ only (degenerate)
  - 71 -> 2+ only (degenerate)
  - 73 -> 2+ only (degenerate)
  - 77 -> 2+ only (degenerate)
  - 93 -> 2+ only (degenerate)
  - 101 -> 2+ only (degenerate)
  - 103 -> 2+ only (degenerate)
  - 105 -> 2+ only (degenerate)
  - 119 -> 2+ only (degenerate)
  - 127 -> 2+ only (degenerate)
  - 139 -> 2+ only (degenerate)
  - 142 -> 2+ only (degenerate)
  - 143 -> 2+ only (degenerate)
  - 150 -> 2+ only (degenerate)
  - 154 -> 2+ only (degenerate)
  - 155 -> 2+ only (degenerate)
  - 158 -> 2+ only (degenerate)
  - 162 -> 2+ only (degenerate)
  - 163 -> 2+ only (degenerate)
  - 172 -> 2+ only (degenerate)
  - 174 -> 2+ only (degenerate)
  - 178 -> 2+ only (degenerate)
  - 179 -> 2+ only (degenerate)
  - 180 -> 2+ only (degenerate)
  - 182 -> 2+ only (degenerate)
  - 187 -> 2+ only (degenerate)
  - 211 -> 2+ only (degenerate)
  - 213 -> 2+ only (degenerate)
  - 214 -> 2+ only (degenerate)
  - 215 -> 2+ only (degenerate)
  - 218 -> 2+ only (degenerate)
  - 219 -> 2+ only (degenerate)
  - 223 -> 2+ only (degenerate)
  - 232 -> 2+ only (degenerate)
  - 234 -> 2+ only (degenerate)
  - 235 -> 2+ only (degenerate)
  - 244 -> 2+ only (degenerate)
  - 246 -> 2+ only (degenerate)
  - 247 -> 2+ only (degenerate)
  - 251 -> 2+ only (degenerate)
  - 254 -> 2+ only (degenerate)
  - 255 -> 2+ only (degenerate)

At `k=8`, the boundary-conditioned split is not a real separator: every 256-bit chunk in the run already contains multiple entry boundaries.
So this stage only tells us the survivors live on boundary-rich windows at that scale; it does not separate boundary effects from interior effects.

## Stage 2

| cell | length-matched | v2-preserving | entry-order shuffle | fair-coin calibration mean |
|---|---|---|---|---:|
| 22 | yes | no | no | 0.003902 |
| 30 | no | no | no | 0.003908 |
| 69 | yes | yes | no | 0.003907 |
| 71 | yes | yes | no | 0.003905 |
| 73 | no | no | no | 0.003914 |
| 77 | yes | no | no | 0.003889 |
| 93 | yes | no | no | 0.003908 |
| 101 | no | no | no | 0.003892 |
| 103 | no | no | no | 0.003921 |
| 105 | no | no | no | 0.003906 |
| 119 | yes | no | no | 0.003905 |
| 127 | no | no | no | 0.003906 |
| 139 | yes | yes | no | 0.003906 |
| 142 | yes | yes | no | 0.003914 |
| 143 | yes | yes | no | 0.003900 |
| 150 | no | no | no | 0.003899 |
| 154 | no | no | no | 0.003907 |
| 155 | no | no | no | 0.003924 |
| 158 | no | no | no | 0.003922 |
| 162 | yes | yes | no | 0.003910 |
| 163 | yes | yes | no | 0.003911 |
| 172 | no | no | no | 0.003887 |
| 174 | no | no | no | 0.003911 |
| 178 | no | no | no | 0.003902 |
| 179 | yes | no | no | 0.003906 |
| 180 | yes | no | no | 0.003919 |
| 182 | yes | no | no | 0.003897 |
| 187 | yes | no | no | 0.003897 |
| 211 | yes | no | no | 0.003882 |
| 213 | yes | no | no | 0.003893 |
| 214 | no | no | no | 0.003911 |
| 215 | no | no | no | 0.003917 |
| 218 | no | no | no | 0.003890 |
| 219 | yes | yes | no | 0.003899 |
| 223 | no | no | no | 0.003906 |
| 232 | yes | no | no | 0.003895 |
| 234 | yes | no | no | 0.003897 |
| 235 | no | no | no | 0.003914 |
| 244 | no | no | no | 0.003908 |
| 246 | yes | no | no | 0.003907 |
| 247 | no | no | no | 0.003921 |
| 251 | yes | no | no | 0.003900 |
| 254 | yes | no | no | 0.003919 |
| 255 | yes | yes | no | 0.003914 |
