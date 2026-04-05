# Mallorn Seed

Ten expeditions into the binary Champernowne of ACMs. Each explores
a phenomenon that only exists — or only becomes visible — when ACM
elements are rendered as bits and concatenated.

All share `binary/binary_core.py` for stream generation, RLE, and
windowed entropy. Each gets a subfolder in `forest/`.


## 1. RLE Spectroscopy

`forest/rle_spectroscopy/`

Generate the binary Champernowne stream for n = 1..256. For each n,
compute the full RLE of the first ~10,000 bits. Plot the run-length
distribution as a heatmap: x-axis is run length (1..20), y-axis is n,
color is frequency. The 2-adic valuation of n should appear as
horizontal ridges — monoids with v_2(n) = 1 cluster together,
v_2(n) = 2 form a sparser band, powers of 2 are singular rows. Odd n
should look qualitatively different from even n, and that difference is
the 2-adic structure becoming visible. The visualization is a
spectrogram of algebraic structure.


## 2. The Tax That Never Closes

`forest/one_bias/`

Track the running fraction of 1-bits in the binary Champernowne stream
as a function of how many n-primes have been concatenated. Plot for
several n values (n = 2, 3, 7, 16, 100). The curve should approach 0.5
from above, with staircase drops at each bit-length boundary. Overlay
the theoretical prediction (d+1)/(2d) as a stepped function. The gap
between theory (over all d-bit integers) and actuality (over n-primes
specifically) is the fingerprint of the sieve — what does n-primality
do to bit balance compared to raw counting?


## 3. Boundary Stitch

`forest/boundary_stitch/`

Zoom into the concatenation boundaries. For a given n, extract a window
of +/-8 bits around every entry boundary in the stream. Stack these
windows vertically to form an image: each row is one boundary, columns
are bit positions relative to the join. The mandatory leading-1 and
trailing-zero structure will appear as vertical stripes. For n = 2^m,
exactly m dark (zero) columns precede a bright (one) column — a barcode
of v_2(n). For odd n, the pattern dissolves into noise. This is the
most direct visualization of boundary algebra.


## 4. Entropy Landscape

`forest/entropy_landscape/`

Compute the Shannon entropy rate of the binary Champernowne stream as a
function of n and window size k (i.e., entropy of k-grams divided by
k). Plot as a surface or heatmap: x = n (1..200), y = k (1..12),
z/color = entropy per bit. A truly random stream has entropy 1.0
everywhere. The deficit from 1.0 is the algebraic content the ACM
structure injects. Where does the deficit concentrate? At small k
(pairwise correlations) or large k (long-range patterns)? Does it
depend on n's factorization?


## 5. The Binary Fabric

`forest/bitfield_quilt/`

The digit fabric experiment, reimagined for bits. Render a large image:
each row is an n-prime (first 800 n-primes of monoid n), each column is
a bit position (MSB at left, padded to max width). Black = 0, white = 1.
The leftmost column is all white. Moving right, columns transition toward
balance. The diagonal weft pattern from the decimal fabric should still
appear, but now it's black-and-white, and the warp threads are
bit-position-dependent. Render for several n side by side to see how the
quilt texture changes with monoid structure.


## 6. Echoes in the Stream

`forest/autocorrelation/`

Compute the autocorrelation function of the binary stream (treating bits
as +1/-1) for lags tau = 1..500. Plot for several n. The autocorrelation
at lag tau measures how predictable bit t+tau is given bit t. Entry
boundaries create periodic spikes at multiples of the average entry
length (which grows logarithmically). As n-primes grow, these spikes
should drift rightward and decay. The decay envelope is the rate at
which the stream "forgets" its concatenation structure.


## 7. Hamming Strata

`forest/hamming_strata/`

Slide a k-bit window across the stream (k = 8, 16, 32). At each
position, compute the Hamming weight (number of 1-bits). Plot the
distribution of Hamming weights. For a fair coin, this is
Binomial(k, 0.5). The deviation from binomial is another way to see the
1-bias, but also to see whether the bias is uniform across windows or
concentrated at specific stream positions (near boundaries, near
bit-length transitions). The Hamming weight distribution is the binary
analog of the digit histogram — but it captures correlations that
single-bit statistics miss.


## 8. The Valuation Forest

`forest/twoadic_tree/`

The most speculative and potentially the most beautiful. For each n from
1 to some limit, compute v_2(n) and use it to organize a tree or
fractal layout. At each leaf, attach a glyph encoding the RLE
fingerprint or entropy deficit of monoid n's binary stream. The result
is a dendrogram of monoids organized by their 2-adic depth, decorated
with their binary Champernowne signatures. Powers of 2 sit at the
deepest branches. Odd numbers are all leaves at depth 0. The visual
question: does 2-adic depth predict stream structure, or are there
surprises?


## 9. The Sawtooth IS Epsilon

`forest/epsilon_teeth/`

Plot the binary Champernowne sawtooth for a single monoid (say n=3,
first 2000 n-primes) alongside the literal epsilon(m) = log_2(1+m) - m
curve. Show they are the same function. Then plot the residual: sawtooth
minus epsilon. Whatever structure survives in that residual is the
contribution of n-primality beyond the positional-notation effect. This
is the experiment that closes the SlideRule bridge.


## 10. Walsh Spectrum

`forest/walsh/`

The Walsh-Hadamard transform is to binary sequences what Fourier is to
continuous signals. Apply it to chunks of the binary Champernowne
stream. Plot the Walsh spectrum. The non-zero coefficients reveal which
Boolean functions of the bit positions carry structure. This is the
natural spectral analysis for the binary setting — not an adaptation
of Fourier, but the native tool.
