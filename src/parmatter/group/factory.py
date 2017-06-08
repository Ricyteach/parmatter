from .meta import FormatGroupMeta
from ..utilities import set_item_if
from .. import VersatileParmatter
import sys
assert (sys.version_info)>(3,6) # required to maintain argument order

def FormatGroup(name, meta=FormatGroupMeta, formatter_type=VersatileParmatter, *, prefix = '', sep = '', **kwargs):
    '''Factory for producing classes that define lines composed of formatting members 
    with optional line prefixes and separators between members. Formatter type must 
    provide a static args_parse() method with a signature of: 
    
        args, kwargs = FormatterType.args_parse(*args)
        f = FormatterType(*args, **kwargs)

    The meta can be a subclass of SpecialAttrsMeta.
    
    Usage:
    
        LineDef = FormatGroup('LineDef', a = '{: 5>s}', prefix = 'my prefix', sep = ', ')
        DefaultLineDef = FormatGroup('DefaultLineDef', a = ('{: 5>s}','foo'), prefix = 'my prefix', sep = ', ')
    '''
    # check the namespace for special item conflicts
    meta.special_check(**kwargs)
    # add special items to the namespace
    factory_specials = '_prefix _sep _formatter_type'.split()
    set_item_if(kwargs, factory_specials, (prefix, sep, formatter_type), lambda o,n,v: v is not None)
    return meta(name, (), kwargs)