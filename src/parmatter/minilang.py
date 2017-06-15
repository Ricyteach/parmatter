import re

regex=r'(([\s\S])?([<>=\^]))?([\+\- ])?([#])?([0])?(\d)*([,])?((\.)(\d)*)?([sbcdoxXneEfFgGn%])?'

from collections import namedtuple as nt
FormatSpec = nt('FormatSpec', 'fill align sign alt zero width comma decimal precision type')

def parse_format_lang(string):
    '''Returns a FormatSpec object built from the provided string conforming to the format
    specification mini language. Raises ValueError if there is no match.'''
    try:
        # skip group numbers not interested in (1, 9)
        return FormatSpec(*re.search(regex, string).group(2,3,4,5,6,7,8,10,11,12)) 
    except AttributeError:
        raise ValueError('The provided format string {} does not conform to the format'
                        'specification mini language.'.format(string)) from None

def create(spec):
    '''Make a format_spec and conversion for use in the extra_types argument of 
    parse.Parse instances.'''
    def f(text):
        return text
    return spec, f