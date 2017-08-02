'''Some custom parmatters useful for various things. See the readme.'''

from .base import ParmatterBase
from ..utilities import args_kwargs_from_args
from ..blank import make_blank
from ..minilang import parse_spec, parse_format_str
import parse as _parse # avoid name conflicts with parse methods
#NOTE: the parse module seems to have some trouble with string fields and spaces around them. don't implicitly trust it. 

class StaticParmatter(ParmatterBase):
    '''A parsing formatter with a designated format string.'''
    def __init__(self, format_str, *args, **kwargs):
        self._format_str = format_str
        self.set_parser(self._format_str, dict(s=str))
        super().__init__(*args, **kwargs)
    def format(self, *args, **kwargs):
        '''ParmatterBase.format overridden to remove format_str from the signature.'''
        return super().format(self._format_str, *args, **kwargs)
    def unformat(self, string):
        '''ParmatterBase.unformat overridden to use compiled parser.'''
        return self._parser.parse(string)
    def set_parser(self, format_str, extra_types=dict(s=str)):
        '''Sets a static parser for the parmatter.'''
        self._parser = _parse.compile(format_str, extra_types)


class FloatIntParmatter(StaticParmatter):
    '''A parsing formatter which has the option of using a new custom spec, "fd".
    The "fd" spec indicates a float value that could also be read as an int. 
    
    Example usage:
        >>> list(FloatIntParmatter().unformat('{:fd}', '1'))
        1.0
        >>> list(FloatIntParmatter().unformat('{:fd}', '1.0'))
        1.0
        >>> FloatIntParmatter().format('{:.1fd}', 1)
        '1.0'
    '''
    def format_field(self, value, spec):
        '''Replace fd with f when formatting is carried out so the the fd
        format behaves exactly like f during formatting.'''
        spec_tup = parse_spec(spec, strict=False)
        spec = spec_tup._replace(type=spec_tup.type.replace('fd', 'f')).join()
        return super().format_field(value, spec)
    # float or int regex
    @staticmethod
    @_parse.with_pattern(r'[+-]?((\.\d+)|(\d+\.\d*)|\d+)')
    def _fd(s):
        '''Method used by the parse module to populate re.Result
        output for the fd formatting spec.
        '''
        return float(s)
    def set_parser(self, format_str, extra_types=dict(s=str)):
        '''Sets a static parser for the parmatter, including new fd spec.'''
        if 'fd' not in extra_types:
            extra_types.update(fd=FloatIntParmatter._fd)
        self._parser = _parse.compile(format_str, extra_types)


class BlankParmatter(StaticParmatter):
    '''A parsing formatter which has the option of using a new custom spec, "blank".
    The "blank" spec indicates a value that could also be read as whitespace. 

    Example usage:
        >>> list(BlankParmatter().unformat('{:dblank}', '1'))
        1
        >>> list(BlankParmatter().unformat('{:dblank}', '            '))
        0
        >>> list(BlankParmatter().unformat('{:fblank}', '1.0'))
        1.0
        >>> BlankParmatter().format('{:.1fblank}', 0.0)
        ' '
        >>> BlankParmatter().format('{:.1fblank}', 1.1)
        '1.1'
    '''
    # regex for "all blank space"
    blank_pattern = r'\s*'
    # for initializing different format type codes, use a mapping to 
    # associate a function decorated by with_pattern(blank_pattern);
    # only used when "blank"
    @staticmethod
    def _blank_handler(f, pattern):
        '''Handler factory for special spec types.'''
        @_parse.with_pattern(pattern)
        def _handler(s):
            if s.split():
                return f(s)
            else:
                return f()
        return _handler
    # to be replaced below:
    def blank_type_to_func(handler_factory, pattern):
        return {k:handler_factory(v, pattern) for k,v in 
                            {'':str, 'fd':float, 's':str,
                             'd':int, 'f':float, 'n':int}.items()}
    # replacing function above:
    blank_type_to_func = blank_type_to_func(_blank_handler.__func__, blank_pattern)
    def format_field(self, value, spec):
        '''Replace value with a Blank object when formatting is carried out. The
        Blank object type knows how to deal with the "blank" spec type. If the value
        is just white space, a blank_initializer based on the spec type is passed
        instead.
        '''
        spec_tup = parse_spec(spec, strict=False)
        if 'blank' in spec_tup.type:
            try:
                # is it a string?
                blanketyblank = value.strip()
            except AttributeError:
                # not a string; no problem
                pass
            else:
                # falsey stripped string?
                if not blanketyblank:
                    # for looking up blank_initializer
                    spec_type = spec_tup.type.replace('blank', '')
                    # replace value (eg 0 for types such as int and float)
                    value = BlankParmatter.blank_type_to_func[spec_type]()
            # falsey objects from make_blank will appear blank when formatted
            value = make_blank(value)
        return super().format_field(value, spec)
    def set_parser(self, format_str, extra_types=dict(s=str)):
        '''Add new blank spec suffixes to the parser's extra_types argument.'''
        # Need to add a different blank spec handler for each of the different kinds of 
        # format spec types (d, n, f, s, etc etc) in the format_str
        # First parse the format_str into usable form (borrowing code from parse module)
        # note: '{{' and '}}' come in from parse_format_str as separate parts
        fields = (part for part in parse_format_str(format_str) 
                   if part and part[0] == '{' and part[-1] == '}')
        # gather the non-blank spec types and add a handler for each
        for field in fields:
            no_brackets = field[1:-1]
            try:
                spec_tup = parse_spec(no_brackets.split(':', 1)[1], strict=False)
            except IndexError:
                raise ValueError('No format specification was provided for the parser.')
            # get version of the spec without the word "blank"
            spec_tup_new = spec_tup._replace(type=spec_tup.type.replace('blank', ''))
            # get the correct with_pattern blank initializer for the spec type
            try:
                blank_initializer = BlankParmatter.blank_type_to_func[spec_tup_new.type]
            except KeyError as err:
                raise KeyError('The spec type {!r} does not have an associated initializer.'
                               ''.format(spec_tup.type)) from err
            # pass the initializer (decorated by with_pattern) to the extra_types dict for the parser
            extra_types.update({spec_tup.type: lambda s: blank_initializer(s)})
        # the original format_str is unaffected
        super().set_parser(format_str, extra_types)


class DefaultParmatter(ParmatterBase):
    '''A parsing formatter with any default namespace.
    
    For keys use ints for indexes of positional arguments, strs
    for fields with names.'''
    def __init__(self, default_namespace, *args, **kwargs):
        self.default_namespace = default_namespace 
        super().__init__(*args, **kwargs)
    def get_value(self, key, args, kwargs):
        try:
            return super().get_value(key, args, kwargs)
        except (KeyError, IndexError) as normal_exc:
            try:
                return self.default_namespace[key]
            except KeyError:
                ExcType = type(normal_exc)
                lookup_type = {KeyError:'key', IndexError:'index'}[ExcType]
                raise ExcType('No default argument was provided for this formatter, {} = {}.'.format(lookup_type, repr(key))) from None
            
class AttrParmatter(ParmatterBase):
    '''A Parmatter that looks in args object attributes for values.
    The args are inspected in order. First one wins. 
    Callable attributes are ignored.'''
    def get_value(self, key, args, kwargs):
        # sentinel marks lookup failure
        sentinel = object()
        # get the normal value
        try:
            value_norm = super().get_value(key, args, kwargs)
        # no value; error stored to be raised later if no attribute value
        except (KeyError, IndexError) as exc:
            value_norm = sentinel
            normal_exc = exc
        # return result if the key can't be an attribute
        else:
            # docs say key is either str or int
            if isinstance(key, int):
                return value_norm
        # assume no attribute values
        value_attr = sentinel
        # look for attribute values
        for arg in args:
            # try to get the attribute value
            value_attr = getattr(arg, key, sentinel)
            # check if found one (no callables!)
            if not callable(value_attr) and value_attr is not sentinel:
                break
            else:
                # discard any methods
                value_attr = sentinel
                continue
        # if no value; raise error as usual
        if value_norm is value_attr is sentinel:
            raise normal_exc
        # if two values, there is an unresolvable name conflict
        if value_norm is not sentinel and value_attr is not sentinel:
            raise ValueError('The name {} is both an attribute of first argument {} object and a key in the keyword arguments. Cannot resolve.'.format(key, type(args[0]).__name__))
        return  {value_norm:value_attr,value_attr:value_norm}[sentinel]
        
class PositionalDefaultParmatter(DefaultParmatter):
    '''A formatter with a default positional namespace.'''
    def __init__(self, *values, default_namespace={}, **kwargs):
        default_namespace.update({i:value for i,value in enumerate(values)})
        super().__init__(default_namespace, **kwargs)
    @staticmethod
    def args_parse(*args):
        '''Form an alternate argument order to create a formatter.
        
        args = '{}', 0,  {a=2, b=3}
        args, kwargs = PositionalDefaultParmatter.args_parse(*args)
        f = PositionalDefaultParmatter(*args, **kwargs)
        '''
        namespace_slice = slice(-1,None,-1)
        args, kwargs = args_kwargs_from_args(args, slc=namespace_slice, asdict=True, ignore_conflicts=True, terminate_on_failure=True)
        kwargs = dict(default_namespace = kwargs)
        return args, kwargs
        
class KeywordParmatter(StaticParmatter,DefaultParmatter,AttrParmatter):
    '''A static formatter with a default keyword namespace that looks in args object 
    attributes for values. The args are inspected in order. First one wins. 
    Callable attributes are ignored.'''
    def __init__(self, format_str, default_namespace, *args, **kwargs):
        super().__init__(format_str, default_namespace, *args, **kwargs)
    
class VersatileParmatter(StaticParmatter,PositionalDefaultParmatter,AttrParmatter):
    '''A static formatter with a default positional namespace that looks in args object 
    attributes for values. The args are inspected in order. First one wins. 
    Callable attributes are ignored.'''
    def __init__(self, format_str, *values, default_namespace={}, **kwargs):
        super().__init__(format_str, *values, default_namespace=default_namespace, **kwargs)