import pytest
from parmatter import Parmatter
import parse as _parse

@pytest.fixture
def SomeFormatter():
    class StaticFormatter(Parmatter):
        '''A parsable formatter with a designated format string.'''
        def __init__(self, format_str, *args, **kwargs):
            self._format_str = format_str
            self._parser = _parse.compile(self._format_str, dict(s=str))
            super().__init__(*args, **kwargs)
        def format(self, *args, **kwargs):
            '''Parmatter.format overridden to remove format_str from the signature.'''
            return super().format(self._format_str, *args, **kwargs)
        def unformat(self, string):
            '''Parmatter.unformat overridden to use compiled parser.'''
            return self._parser.parse(string)
    return StaticFormatter

def test_SomeFormatter(SomeFormatter):
    f=SomeFormatter('{: >5d}')
    assert f.format(1) == '    1'
    assert list(f.unformat('    1')) == [1]