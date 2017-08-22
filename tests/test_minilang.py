from parmatter import minilang as m
import pytest


def test_init():
    x = list(m.parse_format_str('{x[0]}{{{lala:d}{:abc}}}123'))
    assert x == ['{x[0]}', '{{', '{lala:d}', '{:abc}', '}}', '123']
