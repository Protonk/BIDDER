# Experiments

Organized by source object, then by base where base matters.

```
acm-champernowne/   Experiments on ACM-Champernowne streams
  base10/            Decimal digit streams and decimal reals
  base2/             Binary concatenations and binary-derived objects
bidder/              Experiments on BIDDER generator output
math/                Base-generic theory and geometric analysis
future/              Active ideas without a stable home yet
```

## Classification rule

The top-level directory answers "what is the source?" not "what does
the visualization look like?" Art, stats, and other analysis styles
are secondary subdivisions inside the source bucket.

If an experiment's primary source is the ACM-Champernowne construction,
it lives under `acm-champernowne/`. If it uses BIDDER output — even
when comparing to numpy or ACM controls — it lives under `bidder/`.
Theory that is not about one concrete stream family lives under `math/`.

## Key entry points

- [PITCH.md](acm-champernowne/base10/art/PITCH.md) — the five art pieces
- [BINARY.md](acm-champernowne/base2/BINARY.md) — the binary Champernowne argument
- [BIDDER.md](../generator/BIDDER.md) — the generator design
