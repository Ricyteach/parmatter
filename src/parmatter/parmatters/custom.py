'''Some custom parmatters useful for various things. See the readme.'''

from .base import ParmatterBase
from ..utilities import args_kwargs_from_args
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
    def set_parser(self, spec, extra_types=dict(s=str)):
        '''Sets a static parser for the parmatter.'''
        self._parser = _parse.compile(spec, extra_types)


class FloatIntParmatter(StaticParmatter):
    '''A parsing formatter which the option of using a new custom spec, "fd".
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
        '''Replace fd with f when formatting is carried out.'''
        if spec.endswith('fd'):
            spec = spec[:-2] + 'f'
        return super().format_field(value, spec)
    def unformat(self, format, string, extra_types=dict(s=str), evaluate_result=True):
        '''Add the fd spec to possible spec types.'''
        extra_types.update(fd=FloatIntParmatter._fd)
        return super().unformat(format, string, extra_types, evaluate_result)
    # float or int regex
    @_parse.with_pattern(r'[+-]?(((?<!\d)(\.\d+))|(\d+\.\d*)|\d+)')
    @staticmethod
    def _fd(s):
        '''Method used by the parse module to populate re.Result output.
        Requiers the .pattern attribute below to be added. 
        '''
        return float(s)
    def set_parser(self, spec, extra_types=dict(s=str)):
        '''Sets a static parser for the parmatter, including new fd spec.'''
        if 'fd' not in extra_types:
            extra_types.update(fd=FloatIntParmatter._fd)
        self._parser = _parse.compile(spec, extra_types)


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