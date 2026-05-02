"""
test_ff1_nist.py — validate FF1 against NIST SP 800-38G Appendix A.1.

Three AES-128 test vectors from the NIST publication:
  https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-38Gr1-draft.pdf

These vectors are normative; if any fail, the FF1 reference is
broken and §7.4 / D1 numbers must not be reported.

Run via `.venv/bin/python replication/comparators/test_ff1_nist.py`.
"""

import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from comparators.ff1 import Ff1


def hex_to_bytes(h: str) -> bytes:
    return bytes.fromhex(h.replace(' ', ''))


def digits_to_str(d: list[int], radix: int) -> str:
    """Render a digit sequence the way NIST does (0-9 then a-z)."""
    return ''.join('0123456789abcdefghijklmnopqrstuvwxyz'[x] for x in d)


def str_to_digits(s: str, radix: int) -> list[int]:
    return [int(c, 36) for c in s]


def check(name, key_hex, tweak_hex, radix, pt_str, ct_str_expected):
    key = hex_to_bytes(key_hex)
    tweak = hex_to_bytes(tweak_hex)
    pt = str_to_digits(pt_str, radix)
    ff1 = Ff1(key, tweak)
    ct = ff1.encrypt_seq(radix, pt)
    ct_str = digits_to_str(ct, radix)
    ok = ct_str == ct_str_expected
    print(f'{"OK " if ok else "FAIL"}  {name}  expected {ct_str_expected}  got {ct_str}')
    return ok


def main():
    vectors = [
        # NIST SP 800-38G Appendix A.1 Sample 1: AES-128, empty tweak, radix 10
        ('Sample 1 (AES-128, radix=10, empty tweak)',
         '2B7E1516 28AED2A6 ABF71588 09CF4F3C',
         '',
         10,
         '0123456789',
         '2433477484'),
        # Sample 2: AES-128, tweak 39383736353433323130, radix 10
        ('Sample 2 (AES-128, radix=10, tweak)',
         '2B7E1516 28AED2A6 ABF71588 09CF4F3C',
         '39383736353433323130',
         10,
         '0123456789',
         '6124200773'),
        # Sample 3: AES-128, tweak 3737373770717273373737, radix 36
        ('Sample 3 (AES-128, radix=36, tweak)',
         '2B7E1516 28AED2A6 ABF71588 09CF4F3C',
         '3737373770717273373737',
         36,
         '0123456789abcdefghi',
         'a9tv40mll9kdu509eum'),
    ]

    print('FF1 NIST SP 800-38G Appendix A.1 vector validation')
    print('=' * 60)
    all_ok = True
    for name, key, tweak, radix, pt, ct in vectors:
        ok = check(name, key, tweak, radix, pt, ct)
        all_ok = all_ok and ok
    print('=' * 60)
    print('PASS' if all_ok else 'FAIL')
    sys.exit(0 if all_ok else 1)


if __name__ == '__main__':
    main()
