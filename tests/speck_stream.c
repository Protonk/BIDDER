/*
 * speck_stream.c — Raw Speck32/64 in counter mode to stdout.
 *
 * Tests the permutation quality independent of leading-digit extraction.
 * Each counter value is encrypted and written as 4 LE bytes.
 * This is standard counter-mode Speck — should pass PractRand easily.
 *
 * Build: gcc -O2 -o speck_stream tests/speck_stream.c generator/hch.c -lm
 */

#include <stdio.h>
#include <stdint.h>
#include <string.h>

/* Import Speck internals from hch.c */
extern void speck32_expand_key(const uint8_t key[8], uint16_t rk[22]);
extern uint32_t speck32_encrypt(uint32_t pt, const uint16_t rk[22]);

int main(void)
{
    uint8_t seed[] = "Speck32 PractRand";
    /* SHA-256 the seed to get 8 key bytes (reuse from hch.c would be
       nice but let's keep it simple — just use the first 8 bytes) */
    uint8_t key[8];
    /* Simple key derivation: just XOR-fold the seed into 8 bytes */
    memset(key, 0, 8);
    for (int i = 0; i < (int)sizeof(seed) - 1; i++)
        key[i % 8] ^= seed[i];

    uint16_t rk[22];
    speck32_expand_key(key, rk);

    fprintf(stderr, "Speck32/64 counter mode stream\n");

    uint8_t buf[65536];
    int buf_pos = 0;
    uint32_t counter = 0;

    for (;;) {
        uint32_t ct = speck32_encrypt(counter, rk);
        counter++;

        buf[buf_pos++] = (uint8_t)(ct);
        buf[buf_pos++] = (uint8_t)(ct >> 8);
        buf[buf_pos++] = (uint8_t)(ct >> 16);
        buf[buf_pos++] = (uint8_t)(ct >> 24);

        if (buf_pos >= (int)sizeof(buf)) {
            if (fwrite(buf, 1, buf_pos, stdout) != (size_t)buf_pos)
                return 0;
            buf_pos = 0;
        }
    }
}
