'''Tools for parsing the format specification mini language used by the ``format`` built-in function. 
See the string module docs for more information.

The mini language parsing functionality is not exposed in cPython and has therefore been re-implemented 
here.'''

from collections import namedtuple as nt
import re

# only mini-language types
# regex original to me
regex_minilang = r'(([\s\S])?([<>=\^]))?([\+\-])?([#])?([0])?(\d)*([,])?((\.)(\d)*)?([sbcdoxXneEfFgGn%]|$)?'
minilang_parser = re.compile(regex_minilang)

# any type using a-zA-Z for the name
# regex original to me
regex_custom=r'(([\s\S])?([<>=\^]))?([\+\- ])?([#])?([0])?(\d)*([,])?((\.)(\d)*)?([a-zA-Z]+|$)?'
custom_parser = re.compile(regex_custom)

# for parsing any format string with multiple fields
# taken from parse module
regex_format_str = r'({{|}}|{\w*(?:(?:\.\w+)|(?:\[[^\]]+\]))*(?::[^}]+)?})'
format_str_parser = re.compile(regex_format_str)

# for security
# taken from parse module
safety_parser = re.compile(r'([?\\\\.[\]()*+\^$!\|])')


_FormatSpec = nt('FormatSpecBase', 'fill align sign alt zero width comma decimal precision type')

class FormatSpec(_FormatSpec):
    __slots__ = ()
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

def parse_spec(spec, strict=True):
    '''Returns a FormatSpec object built from the provided string conforming to the format
    specification mini language. Raises ValueError if there is no match.'''
    parse_picker = {True: minilang_parser, False: custom_parser}
    parser = parse_picker[strict]
    match = parser.fullmatch(spec)
    try:
        # skip group numbers not interested in (1, 9)
        return FormatSpec(*match.group(2,3,4,5,6,7,8,10,11,12))
    except AttributeError:
        raise ValueError('The provided format specification string {!r} does '
                         'not conform to the format specification mini language.'
                         ''.format(spec)) from None

SpecConvert = nt('SpecConvert', 'spec converter')

def define(spec):
    '''Make a (format_spec, conversion) tuple for use in the extra_types argument of 
    parse.Parse instances.'''
    spec_def=parse_spec(spec)
    spec_type=spec_def.type
    spec_type=spec_def.type
    def general(text):
        if spec_def.width != len(text):
            return None
        if spec_def.align:
            fill=spec_def.fill if spec_def.fill else ' '
            sign=spec_def.sign if spec_def.sign else ''
    def f(text):
        return float(text)
    def d(text):
        return int(text)
    def s(test):
        return str(text)
    return SpecConvert(spec, dict(f=f, d=d, s=s)[spec_type])

def parse_format_str(format_str):
    '''Generates format string fields.'''
    # much of this code taken from parse module
    for part in format_str_parser.split(format_str):
        if not part:
            continue
        elif part in ('{{', '}}') or part[0] == '{':
            yield part
        else:
            yield safety_parser.sub(lambda match: '\\' + match.group(1), part)
