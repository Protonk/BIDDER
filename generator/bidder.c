/*
 * bidder.c — BIDDER block generator (C implementation)
 *
 * Stupid simple. One file, one struct, three functions. Speck32/64 for
 * tight-fit blocks, balanced Feistel for small blocks. SHA-256 for key
 * derivation (bundled below, no external deps).
 */

#include "bidder.h"
#include <string.h>

/* ================================================================
 * Minimal SHA-256 (for key derivation only — not performance critical)
 * ================================================================ */

static const uint32_t sha256_k[64] = {
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,
    0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,
    0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,
    0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,
    0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,
    0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,
    0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,
    0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,
    0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
};

#define RR32(x,n) (((x)>>(n))|((x)<<(32-(n))))

static void sha256_transform(uint32_t h[8], const uint8_t block[64])
{
    uint32_t w[64], a,b,c,d,e,f,g,hh,t1,t2;
    int i;
    for (i = 0; i < 16; i++)
        w[i] = ((uint32_t)block[i*4]<<24) | ((uint32_t)block[i*4+1]<<16) |
               ((uint32_t)block[i*4+2]<<8) | block[i*4+3];
    for (i = 16; i < 64; i++) {
        uint32_t s0 = RR32(w[i-15],7)^RR32(w[i-15],18)^(w[i-15]>>3);
        uint32_t s1 = RR32(w[i-2],17)^RR32(w[i-2],19)^(w[i-2]>>10);
        w[i] = w[i-16]+s0+w[i-7]+s1;
    }
    a=h[0]; b=h[1]; c=h[2]; d=h[3]; e=h[4]; f=h[5]; g=h[6]; hh=h[7];
    for (i = 0; i < 64; i++) {
        uint32_t S1 = RR32(e,6)^RR32(e,11)^RR32(e,25);
        uint32_t ch = (e&f)^((~e)&g);
        t1 = hh+S1+ch+sha256_k[i]+w[i];
        uint32_t S0 = RR32(a,2)^RR32(a,13)^RR32(a,22);
        uint32_t maj = (a&b)^(a&c)^(b&c);
        t2 = S0+maj;
        hh=g; g=f; f=e; e=d+t1; d=c; c=b; b=a; a=t1+t2;
    }
    h[0]+=a; h[1]+=b; h[2]+=c; h[3]+=d;
    h[4]+=e; h[5]+=f; h[6]+=g; h[7]+=hh;
}

static void sha256(const uint8_t *data, uint32_t len, uint8_t out[32])
{
    uint32_t h[8] = {
        0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
        0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19
    };
    uint8_t block[64];
    uint32_t i, blocks, rem;

    /* Full blocks */
    blocks = len / 64;
    for (i = 0; i < blocks; i++)
        sha256_transform(h, data + i * 64);

    /* Padding */
    rem = len % 64;
    memset(block, 0, 64);
    memcpy(block, data + blocks * 64, rem);
    block[rem] = 0x80;
    if (rem >= 56) {
        sha256_transform(h, block);
        memset(block, 0, 64);
    }
    uint64_t bitlen = (uint64_t)len * 8;
    for (i = 0; i < 8; i++)
        block[56 + i] = (uint8_t)(bitlen >> (56 - i * 8));
    sha256_transform(h, block);

    for (i = 0; i < 8; i++) {
        out[i*4]   = (uint8_t)(h[i]>>24);
        out[i*4+1] = (uint8_t)(h[i]>>16);
        out[i*4+2] = (uint8_t)(h[i]>>8);
        out[i*4+3] = (uint8_t)(h[i]);
    }
}


/* ================================================================
 * Speck32/64
 * ================================================================ */

#define ROR16(x,r) ((uint16_t)(((x)>>(r))|((x)<<(16-(r)))))
#define ROL16(x,r) ((uint16_t)(((x)<<(r))|((x)>>(16-(r)))))

void speck32_expand_key(const uint8_t key[8], uint16_t rk[22])
{
    uint16_t k = (uint16_t)(key[0] | (key[1] << 8));
    uint16_t l[24]; /* max index: i+3 for i=0..20 = 23 */
    l[0] = (uint16_t)(key[2] | (key[3] << 8));
    l[1] = (uint16_t)(key[4] | (key[5] << 8));
    l[2] = (uint16_t)(key[6] | (key[7] << 8));

    rk[0] = k;
    for (int i = 0; i < 21; i++) {
        l[i + 3] = (uint16_t)((ROR16(l[i], 7) + k) ^ i);
        k = (uint16_t)(ROL16(k, 2) ^ l[i + 3]);
        rk[i + 1] = k;
    }
}

uint32_t speck32_encrypt(uint32_t pt, const uint16_t rk[22])
{
    uint16_t x = (uint16_t)(pt >> 16);
    uint16_t y = (uint16_t)(pt & 0xFFFF);
    for (int i = 0; i < 22; i++) {
        x = (uint16_t)(ROR16(x, 7) + y);
        x ^= rk[i];
        y = (uint16_t)(ROL16(y, 2) ^ x);
    }
    return ((uint32_t)x << 16) | y;
}


/* ================================================================
 * BIDDER generator
 * ================================================================ */

static uint64_t ipow(uint64_t base, uint32_t exp, int *overflow)
{
    uint64_t result = 1;
    for (uint32_t i = 0; i < exp; i++) {
        if (base != 0 && result > UINT64_MAX / base) {
            *overflow = 1;
            return 0;
        }
        result *= base;
    }
    *overflow = 0;
    return result;
}

static uint32_t isqrt_ceil(uint64_t n)
{
    if (n == 0) return 0;
    /* Integer Newton's method — no floating point */
    uint64_t s = 1;
    while (s * s < n)
        s = (s + n / s) / 2 + 1; /* +1 ensures ceiling and convergence */
    /* Back off if we overshot */
    while (s > 0 && (s - 1) * (s - 1) >= n)
        s--;
    return (uint32_t)s;
}

static uint32_t leading_digit(uint64_t n, uint64_t base)
{
    while (n >= base)
        n /= base;
    return (uint32_t)n;
}

int bidder_init(bidder_ctx *ctx, uint64_t base, uint32_t digit_class,
             const uint8_t *key, uint32_t key_len)
{
    if (base < 2 || digit_class < 1)
        return -1;

    memset(ctx, 0, sizeof(*ctx));
    ctx->base = base;
    ctx->digit_class = digit_class;

    int ov1, ov2;
    ctx->block_start = ipow(base, digit_class - 1, &ov1);
    uint64_t block_end = ipow(base, digit_class, &ov2);
    if (ov1 || ov2)
        return -1;  /* overflow — base^digit_class exceeds uint64 */
    block_end -= 1;
    ctx->block_size = block_end - ctx->block_start + 1;
    ctx->counter = 0;

    if (ctx->block_size > (uint64_t)UINT32_MAX + 1)
        return -1;  /* too large for Speck32 */

    uint64_t speck_block = (uint64_t)1 << 32;

    if (speck_block <= (uint64_t)BIDDER_MAX_CYCLE_WALK_RATIO * ctx->block_size) {
        /* Speck32/64 mode */
        ctx->mode = 0;
        uint8_t hash[32];
        sha256(key, key_len, hash);
        speck32_expand_key(hash, ctx->speck_rk);
    } else {
        /* Feistel mode */
        ctx->mode = 1;
        uint32_t s = isqrt_ceil(ctx->block_size);
        ctx->L_size = s;
        ctx->R_size = s;

        /* Hash the full key once, then derive round keys from the hash */
        uint8_t key_hash[32];
        sha256(key, key_len, key_hash);
        for (int i = 0; i < BIDDER_FEISTEL_ROUNDS; i++) {
            uint8_t buf[36]; /* 32-byte hash + 4-byte index */
            memcpy(buf, key_hash, 32);
            buf[32] = (uint8_t)(i);
            buf[33] = (uint8_t)(i >> 8);
            buf[34] = (uint8_t)(i >> 16);
            buf[35] = (uint8_t)(i >> 24);

            uint8_t round_hash[32];
            sha256(buf, 36, round_hash);
            ctx->feistel_keys[i] = 0;
            for (int j = 0; j < 8; j++)
                ctx->feistel_keys[i] |= (uint64_t)round_hash[j] << (j * 8);
        }
    }
    return 0;
}

static uint32_t permute_speck(const bidder_ctx *ctx, uint32_t index)
{
    uint32_t val = index;
    for (;;) {
        val = speck32_encrypt(val, ctx->speck_rk);
        if (val < (uint32_t)ctx->block_size)
            return val;
    }
}

static uint32_t permute_feistel(const bidder_ctx *ctx, uint32_t index)
{
    uint32_t L_size = ctx->L_size;
    uint32_t R_size = ctx->R_size;

    for (;;) {
        uint32_t L = index / R_size;
        uint32_t R = index % R_size;

        for (int i = 0; i < BIDDER_FEISTEL_ROUNDS; i++) {
            uint64_t rk = ctx->feistel_keys[i];
            uint32_t f = (uint32_t)(((R + (rk >> (i * 3))) ^
                                     (rk >> (i * 5 + 1))) % L_size);
            uint32_t tmp = R;
            R = (L + f) % L_size;
            L = tmp;
        }

        uint32_t result = L * R_size + R;
        if (result < (uint32_t)ctx->block_size)
            return result;
        index = result;
    }
}

uint32_t bidder_next(bidder_ctx *ctx)
{
    if (ctx->counter >= ctx->block_size)
        ctx->counter = 0;

    uint32_t perm;
    if (ctx->mode == 0)
        perm = permute_speck(ctx, (uint32_t)ctx->counter);
    else
        perm = permute_feistel(ctx, (uint32_t)ctx->counter);

    ctx->counter++;
    uint64_t n = ctx->block_start + perm;
    return leading_digit(n, ctx->base);
}

void bidder_reset(bidder_ctx *ctx)
{
    ctx->counter = 0;
}
