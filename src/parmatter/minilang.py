'''Tools for parsing the format specification mini language used by the ``format`` built-in function. 
See the string module docs for more information.
 
The mini language parsing functionality is not exposed in cPython and has therefore been re-implemented 
here.'''

from collections import namedtuple as nt
import re

regex=r'(([\s\S])?([<>=\^]))?([\+\- ])?([#])?([0])?(\d)*([,])?((\.)(\d)*)?([sbcdoxXneEfFgGn%])?'
reparser=re.compile(regex)

_FormatSpec = nt('FormatSpecBase', 'fill align sign alt zero width comma decimal precision type')

class FormatSpec(_FormatSpec):
    def __new__(cls, fill, align, sign, alt, zero, width, comma, decimal, precision, type):
        to_int=lambda x: int(x) if x is not None else x
        zero=to_int(zero)
        width=to_int(width)
        precision=to_int(precision)
        return super().__new__(cls, fill, align, sign, alt, zero, width, comma, decimal, precision, type)
    def join(self):
        return ''.join('{!s}'.format(s) for s in self if s is not None)
    def __format__(self, format_spec):
        try:
            return format(self.join(), format_spec)
        except (TypeError, ValueError):
            return super().__format__(format_spec)
        
FormatSpec.__doc__=_FormatSpec.__doc__.replace('FormatSpecBase','FormatSpec')
FormatSpec.__new__.__doc__=_FormatSpec.__new__.__doc__.replace('FormatSpecBase','FormatSpec')

def parse_spec(spec):
    '''Returns a FormatSpec object built from the provided string conforming to the format
    specification mini language. Raises ValueError if there is no match.'''
    try:
        # skip group numbers not interested in (1, 9)
        return FormatSpec(*reparser.fullmatch(spec).group(2,3,4,5,6,7,8,10,11,12))
    except AttributeError:
        raise ValueError('The provided format string {!r} does not conform to the format'
                        'specification mini language.'.format(spec)) from None