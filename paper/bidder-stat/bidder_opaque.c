/*
 * bidder_opaque.c — Opaque FFI wrappers for libbidder.
 *
 * Each handle is a heap-allocated copy of the real struct. The ctypes
 * wrapper never sees the layout; it passes and receives void pointers.
 *
 * The cipher path delegates to bidder_root.c (pure delegation).
 *
 * The sawtooth path reimplements the Hardy closed form using __int128
 * instead of delegating to bidder_sawtooth_at(), which returns
 * uint64_t and reports overflow for results above 2^64. The opaque
 * API needs the wider (lo, hi) output to match the Python contract.
 * Both implementations compute the same formula; they differ only in
 * output width.
 */

#include "bidder_opaque.h"
#include "bidder_root.h"

#include <stdlib.h>
#include <string.h>

/* ---- Cipher path ------------------------------------------------- */

struct bdo_block {
    bidder_block_ctx ctx;
};

bdo_block *bdo_block_create(uint64_t period,
                             const uint8_t *key, size_t key_len,
                             int *err)
{
    bdo_block *h;
    int rc;

    if (err == NULL)
        return NULL;

    h = (bdo_block *)malloc(sizeof(*h));
    if (h == NULL) {
        *err = BIDDER_ROOT_ERR_NULL;
        return NULL;
    }
    memset(h, 0, sizeof(*h));

    rc = bidder_cipher_init(&h->ctx, period, key, key_len);
    if (rc != BIDDER_ROOT_OK) {
        free(h);
        *err = rc;
        return NULL;
    }

    *err = BIDDER_ROOT_OK;
    return h;
}

void bdo_block_free(bdo_block *h)
{
    free(h);  /* NULL-safe per C standard */
}

int bdo_block_at(const bdo_block *h, uint64_t i, uint32_t *out)
{
    if (h == NULL || out == NULL)
        return BIDDER_ROOT_ERR_NULL;
    return bidder_block_at(&h->ctx, i, out);
}

uint64_t bdo_block_period(const bdo_block *h)
{
    if (h == NULL)
        return 0;
    return h->ctx.period;
}

const char *bdo_block_backend(const bdo_block *h)
{
    if (h == NULL)
        return NULL;
    return bidder_block_backend(&h->ctx);
}

/* ---- Sawtooth path ----------------------------------------------- */

struct bdo_nprime {
    nprime_sequence_ctx ctx;
};

bdo_nprime *bdo_nprime_create(uint64_t n, uint64_t count, int *err)
{
    bdo_nprime *h;
    int rc;

    if (err == NULL)
        return NULL;

    h = (bdo_nprime *)malloc(sizeof(*h));
    if (h == NULL) {
        *err = BIDDER_ROOT_ERR_NULL;
        return NULL;
    }
    memset(h, 0, sizeof(*h));

    rc = bidder_sawtooth_init(&h->ctx, n, count);
    if (rc != BIDDER_ROOT_OK) {
        free(h);
        *err = rc;
        return NULL;
    }

    *err = BIDDER_ROOT_OK;
    return h;
}

void bdo_nprime_free(bdo_nprime *h)
{
    free(h);
}

int bdo_nprime_at(const bdo_nprime *h, uint64_t i,
                  uint64_t *out_lo, uint64_t *out_hi)
{
    __uint128_t q, r, inner, result;

    if (h == NULL || out_lo == NULL || out_hi == NULL)
        return BIDDER_ROOT_ERR_NULL;
    if (h->ctx.n < 2 || h->ctx.count < 1)
        return BIDDER_ROOT_ERR_BACKEND;
    if (i >= h->ctx.count)
        return BIDDER_ROOT_ERR_INDEX;

    q = (__uint128_t)i / (h->ctx.n - 1);
    r = (__uint128_t)i % (h->ctx.n - 1);
    inner = q * (__uint128_t)h->ctx.n + r + 1;
    result = (__uint128_t)h->ctx.n * inner;

    *out_lo = (uint64_t)result;
    *out_hi = (uint64_t)(result >> 64);
    return BIDDER_ROOT_OK;
}

uint64_t bdo_nprime_n(const bdo_nprime *h)
{
    if (h == NULL)
        return 0;
    return h->ctx.n;
}

uint64_t bdo_nprime_count(const bdo_nprime *h)
{
    if (h == NULL)
        return 0;
    return h->ctx.count;
}
