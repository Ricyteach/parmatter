import pytest
from parmatter import Parmatter
import parse as _parse

@pytest.fixture
def SomeFormatter():
    class AFormatter(Parmatter):
        pass
    return AFormatter

def test_SomeFormatter(SomeFormatter):
    f=SomeFormatter()
    assert f.format('{: >5d}', 1) == '    1'
    assert list(f.unformat('{: >5d}', '    1')) == [1]    
    
@pytest.fixture
def OverriddenFormatters():
    class formatOverride(Parmatter):
        def format(self, *args, **kwargs):
            return super().format(*args, **kwargs)
    class vformatOverride(Parmatter):
        def vformat(self, *args, **kwargs):
            return super().vformat(*args, **kwargs)
    class _vformatOverride(Parmatter):
        def _vformat(self, *args, **kwargs):
            return super()._vformat(*args, **kwargs)
    class parseOverride(Parmatter):
        def parse(self, *args, **kwargs):
            return super().parse(*args, **kwargs)
    class get_fieldOverride(Parmatter):
        def get_field(self, *args, **kwargs):
            return super().get_field(*args, **kwargs)
    class get_valueOverride(Parmatter):
        def get_value(self, *args, **kwargs):
            return super().get_value(*args, **kwargs)
    class check_unused_argsOverride(Parmatter):
        def check_unused_args(self, *args, **kwargs):
            super().check_unused_args(*args, **kwargs)
    class format_fieldOverride(Parmatter):
        def format_field(self, *args, **kwargs):
            return super().format_field(*args, **kwargs)
    class convert_fieldOverride(Parmatter):
        def convert_field(self, *args, **kwargs):
            return super().convert_field(*args, **kwargs)
    return locals()

def test_SomeFormatters(OverriddenFormatters):
    classes_dict = OverriddenFormatters
    objs_dict= ((name, cls()) for name,cls in classes_dict.items())
    for name, f in objs_dict:
        assert f.format('{: >5d}', 1) == '    1'