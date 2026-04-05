/*
 * bidder_stream.c — Emit raw bytes from the BIDDER generator to stdout.
 *
 * For piping to PractRand's RNG_test:
 *   ./bidder_stream | RNG_test stdin
 *
 * Uses base 65536, digit_class 2 (tight Speck32 fit, period ~4.3G).
 * Each output symbol d in {1..65535} is written as 2 little-endian bytes.
 * Wraps at period boundary and rekeys for the next period.
 *
 * Build: gcc -O2 -o bidder_stream tests/bidder_stream.c generator/bidder.c -lm
 */

#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "../generator/bidder.h"

int main(void)
{
    bidder_ctx ctx;
    uint64_t base = 65536;
    uint32_t digit_class = 2;
    uint8_t key[] = "BIDDER PractRand test";
    uint32_t key_len = sizeof(key) - 1;

    int rc = bidder_init(&ctx, base, digit_class, key, key_len);
    if (rc != 0) {
        fprintf(stderr, "bidder_init failed\n");
        return 1;
    }

    fprintf(stderr, "BIDDER stream: base=%llu d=%u period=%llu mode=%s\n",
            (unsigned long long)base, digit_class,
            (unsigned long long)ctx.block_size,
            ctx.mode == 0 ? "speck32" : "feistel");

    /* Buffer output for performance */
    uint8_t buf[65536];
    int buf_pos = 0;
    uint64_t total = 0;
    uint32_t rekey_count = 0;

    for (;;) {
        uint32_t d = bidder_next(&ctx);

        /* Write symbol as 2 little-endian bytes */
        buf[buf_pos++] = (uint8_t)(d & 0xFF);
        buf[buf_pos++] = (uint8_t)((d >> 8) & 0xFF);

        if (buf_pos >= (int)sizeof(buf)) {
            if (fwrite(buf, 1, buf_pos, stdout) != (size_t)buf_pos)
                return 0;  /* broken pipe = normal exit */
            buf_pos = 0;
        }

        total++;

        /* Rekey at period boundary for infinite stream */
        if (total % ctx.block_size == 0) {
            rekey_count++;
            uint8_t new_key[64];
            memcpy(new_key, key, key_len);
            new_key[key_len]   = (uint8_t)(rekey_count);
            new_key[key_len+1] = (uint8_t)(rekey_count >> 8);
            new_key[key_len+2] = (uint8_t)(rekey_count >> 16);
            new_key[key_len+3] = (uint8_t)(rekey_count >> 24);
            bidder_init(&ctx, base, digit_class, new_key, key_len + 4);

            fprintf(stderr, "  rekey #%u at %llu bytes\n",
                    rekey_count, total * 2);
        }
    }
}
