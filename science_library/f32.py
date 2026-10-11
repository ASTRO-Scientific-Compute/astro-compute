"""Independent exact-rational oracle for finite, canonical-zero binary32.

No host floating arithmetic is used by scientific +,-,*,/,sqrt. GPU uses
bounded integer significands; this oracle uses unbounded rational numbers.
"""
from fractions import Fraction
from functools import lru_cache
import re
import struct

ONE = 0x3f800000
HALF = 0x3f000000
TWO = 0x40000000


def parse(value):
    if not isinstance(value, str) or re.fullmatch(r'[0-9a-fA-F]{8}', value) is None:
        raise ValueError('binary32 input requires exactly eight hex digits')
    bits = int(value, 16)
    if bits & 0x7f800000 == 0x7f800000:
        raise ValueError('nonfinite binary32 input')
    return bits


def hex32(value):
    """Explicit conversion utility for exactly representable Python numbers only."""
    if type(value) not in (int, float):
        raise ValueError('expected exact finite number')
    bits = int.from_bytes(struct.pack('<f', value), 'little')
    if rational(bits) != Fraction(value):
        raise ValueError('not exactly representable: supply explicitly rounded binary32 bits')
    return f'{bits:08x}'


@lru_cache(maxsize=32768)
def rational(bits):
    exponent = (bits >> 23) & 255
    if exponent == 255:
        raise ValueError('nonfinite binary32')
    mantissa = (bits & 0x7fffff) | (0x800000 if exponent else 0)
    power = max(exponent, 1) - 150
    value = Fraction(mantissa << power) if power >= 0 else Fraction(mantissa, 1 << -power)
    return -value if bits >> 31 else value


def power2(exponent):
    return Fraction(1 << exponent) if exponent >= 0 else Fraction(1, 1 << -exponent)


def rounded(value):
    value = Fraction(value)
    if not value:
        return 0
    sign = 0x80000000 if value < 0 else 0
    value = abs(value)
    exponent = value.numerator.bit_length() - value.denominator.bit_length()
    if value < power2(exponent):
        exponent -= 1
    step = power2(max(exponent - 23, -149))
    scaled = value / step
    q, remainder = divmod(scaled.numerator, scaled.denominator)
    if 2 * remainder > scaled.denominator or (2 * remainder == scaled.denominator and q & 1):
        q += 1
    if not q:
        return 0
    if exponent < -126:
        return sign | q
    if q == 1 << 24:
        q >>= 1
        exponent += 1
    if exponent > 127:
        raise ValueError('binary32 intermediate overflow')
    return sign | ((exponent + 127) << 23) | (q - (1 << 23))


def add(a, b):
    return rounded(rational(a) + rational(b))


def neg(a):
    return a ^ 0x80000000 if a & 0x7fffffff else 0


def sub(a, b):
    return add(a, neg(b))


def mul(a, b):
    return rounded(rational(a) * rational(b))


def div(a, b):
    if not rational(b):
        raise ValueError('binary32 zero denominator')
    return rounded(rational(a) / rational(b))


@lru_cache(maxsize=32768)
def sqrt(a):
    x = rational(a)
    if x < 0:
        raise ValueError('negative root')
    if not x:
        return 0
    # Binary search adjacent representable numbers, then compare the exact
    # midpoint squared. Independent of the GPU digit-by-digit integer root.
    lo, hi = 0, 0x7f7fffff
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if rational(mid) ** 2 <= x:
            lo = mid
        else:
            hi = mid - 1
    if rational(lo) ** 2 == x:
        return lo
    midpoint = (rational(lo) + rational(lo + 1)) / 2
    return lo + int(x > midpoint ** 2 or (x == midpoint ** 2 and lo & 1))


def summation(values):
    total = 0
    for value in values:
        total = add(total, value)
    return total


def dot(a, b):
    return summation(mul(x, y) for x, y in zip(a, b))
