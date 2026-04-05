/*
 * acm_core.c — ACM-Champernowne core definitions (C implementation)
 *
 * Shot-for-shot remake of acm_core.py. Same functions, same results,
 * different language. The Python and C implementations form two
 * vertices of the DOCS::C::PYTHON audit triangle.
 */

#include "acm_core.h"
#include <math.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>


/* -----------------------------------------------------------------
 * n-prime generation
 * ----------------------------------------------------------------- */

int acm_n_primes(int n, int count, int *out)
{
    if (n < 1 || count < 1 || out == NULL)
        return -1;

    if (n == 1) {
        /* Ordinary primes by trial division. */
        int found = 0;
        int candidate = 2;
        while (found < count) {
            int is_prime = 1;
            for (int i = 0; i < found; i++) {
                if (candidate % out[i] == 0) {
                    is_prime = 0;
                    break;
                }
            }
            if (is_prime)
                out[found++] = candidate;
            candidate++;
        }
        return 0;
    }

    /* n >= 2: elements n*k where k is not divisible by n. */
    int found = 0;
    int k = 1;
    while (found < count) {
        if (k % n != 0)
            out[found++] = n * k;
        k++;
    }
    return 0;
}


/* -----------------------------------------------------------------
 * Digit counting (decimal digits in an integer)
 * ----------------------------------------------------------------- */

static int int_digit_count(int x)
{
    if (x <= 0) return 1;
    int d = 0;
    while (x > 0) { d++; x /= 10; }
    return d;
}


/* -----------------------------------------------------------------
 * Champernowne real
 *
 * Precision: the concatenated string is parsed as an IEEE 754 double
 * via strtod(). Only the first ~16 significant decimal digits of the
 * fractional part survive the conversion. For large n or large count,
 * the trailing n-primes contribute nothing to the returned value.
 * This caps effective precision at ~53 bits. The leading-digit
 * property (which needs 1 digit) and the sawtooth structure (which
 * needs ~10) are unaffected.
 * ----------------------------------------------------------------- */

double acm_champernowne_real(int n, int count)
{
    if (n < 1 || count < 1)
        return 0.0;

    int *primes = malloc(count * sizeof(int));
    if (!primes) return 0.0;
    acm_n_primes(n, count, primes);

    /*
     * Build "1." + concatenated decimal representations.
     * Max digits per prime is ~10 (for int range), so a 2048-char
     * buffer is generous for any reasonable count.
     */
    char buf[2048];
    buf[0] = '1';
    buf[1] = '.';
    int pos = 2;

    for (int i = 0; i < count; i++) {
        int written = snprintf(buf + pos, sizeof(buf) - pos, "%d", primes[i]);
        pos += written;
        if (pos >= (int)sizeof(buf) - 1) break;
    }
    buf[pos] = '\0';

    free(primes);
    return strtod(buf, NULL);
}


/* -----------------------------------------------------------------
 * Digit count
 * ----------------------------------------------------------------- */

int acm_digit_count(int n, int count)
{
    if (n < 1 || count < 1)
        return -1;

    int *primes = malloc(count * sizeof(int));
    if (!primes) return -1;
    acm_n_primes(n, count, primes);

    int total = 0;
    for (int i = 0; i < count; i++)
        total += int_digit_count(primes[i]);

    free(primes);
    return total;
}


/* -----------------------------------------------------------------
 * First-digit extraction
 * ----------------------------------------------------------------- */

int acm_first_digit(double x)
{
    if (x <= 0.0)
        return 0;
    double l = log10(x);
    double frac = l - floor(l);
    int d = (int)(pow(10.0, frac) + 1e-9);
    if (d > 9) d = 9;
    return d;
}


/* -----------------------------------------------------------------
 * Benford reference
 *
 * Returns the Benford probability for a single digit d in [1, 9]:
 * log10(1 + 1/d). Takes the digit as an argument and returns a
 * scalar, so callers can request exactly the digit they need
 * without allocating an array. Typical use: compare an observed
 * frequency against acm_benford(d) in a loop over d = 1..9.
 * ----------------------------------------------------------------- */

double acm_benford(int d)
{
    if (d < 1 || d > 9)
        return 0.0;
    return log10(1.0 + 1.0 / d);
}
