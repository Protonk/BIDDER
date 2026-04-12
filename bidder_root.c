/*
 * bidder_root.c — C twin of the project-root bidder.py entry point.
 */

#include "bidder_root.h"

#include <limits.h>
#include <string.h>


int bidder_cipher_init(
    bidder_block_ctx *ctx,
    uint64_t period,
    const uint8_t *key,
    size_t key_len
)
{
    static const uint8_t empty_key[1] = {0};

    if (ctx == NULL)
        return BIDDER_ROOT_ERR_NULL;

    memset(ctx, 0, sizeof(*ctx));

    if (period < 2)
        return BIDDER_ROOT_ERR_PERIOD;
    if (period > BIDDER_ROOT_MAX_PERIOD_V1)
        return BIDDER_ROOT_ERR_UNSUPPORTED_PERIOD;
    if (key == NULL && key_len != 0)
        return BIDDER_ROOT_ERR_NULL;
    if (key_len > UINT32_MAX)
        return BIDDER_ROOT_ERR_KEY_LENGTH;
    if (key == NULL)
        key = empty_key;

    ctx->period = period;
    if (bidder_init(&ctx->inner, period + 1, 1, key, (uint32_t)key_len) != 0) {
        memset(ctx, 0, sizeof(*ctx));
        return BIDDER_ROOT_ERR_BACKEND;
    }
    return BIDDER_ROOT_OK;
}


int bidder_block_at(const bidder_block_ctx *ctx, uint64_t i, uint32_t *out)
{
    uint32_t raw;

    if (ctx == NULL || out == NULL)
        return BIDDER_ROOT_ERR_NULL;
    if (ctx->period < 2)
        return BIDDER_ROOT_ERR_BACKEND;
    if (i >= ctx->period)
        return BIDDER_ROOT_ERR_INDEX;

    raw = bidder_at(&ctx->inner, i);
    if (raw == 0 || raw > ctx->period)
        return BIDDER_ROOT_ERR_BACKEND;

    *out = raw - 1;
    return BIDDER_ROOT_OK;
}


const char *bidder_block_backend(const bidder_block_ctx *ctx)
{
    if (ctx == NULL)
        return NULL;
    return ctx->inner.mode == 0 ? "speck32" : "feistel";
}


int bidder_sawtooth_init(nprime_sequence_ctx *ctx, uint64_t n, uint64_t count)
{
    if (ctx == NULL)
        return BIDDER_ROOT_ERR_NULL;

    memset(ctx, 0, sizeof(*ctx));

    if (n < 2)
        return BIDDER_ROOT_ERR_N;
    if (count < 1)
        return BIDDER_ROOT_ERR_COUNT;

    ctx->n = n;
    ctx->count = count;
    return BIDDER_ROOT_OK;
}


int bidder_sawtooth_at(const nprime_sequence_ctx *ctx, uint64_t i, uint64_t *out)
{
    uint64_t q;
    uint64_t r;
    uint64_t inner;

    if (ctx == NULL || out == NULL)
        return BIDDER_ROOT_ERR_NULL;
    if (ctx->n < 2 || ctx->count < 1)
        return BIDDER_ROOT_ERR_BACKEND;
    if (i >= ctx->count)
        return BIDDER_ROOT_ERR_INDEX;

    q = i / (ctx->n - 1);
    r = i % (ctx->n - 1);

    if (q > (UINT64_MAX - (r + 1)) / ctx->n)
        return BIDDER_ROOT_ERR_OVERFLOW;
    inner = q * ctx->n + r + 1;

    if (inner > UINT64_MAX / ctx->n)
        return BIDDER_ROOT_ERR_OVERFLOW;

    *out = ctx->n * inner;
    return BIDDER_ROOT_OK;
}
