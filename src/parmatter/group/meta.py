from ..utilities import args_kwargs_from_args
from collections import OrderedDict as od, namedtuple as nt
import parse

class SpecialAttrsMeta(type):
    '''A base metaclass that removes special attribute names from the namespace
    prior to passing them for initialization.
    Special attributes are designated by the attribute "_special".
    Any _special attributes not defined at runtime are ignored.'''
    def __new__(mcls, name, bases, mapping):
        cls = super().__new__(mcls,name,bases,mapping)
        sentinel = object()
        reserved_mapping = {n:mapping.pop(n, sentinel) for n in mcls._special}
        for k,v in ((k,v) for k,v in reserved_mapping.items() if v is not sentinel):
            setattr(cls, k, v)
        return cls
    @classmethod
    def special_check(meta, **kwargs):
        '''Check to make sure there are no conflicts with special attribute names.'''
        try:
            special = meta._special
            # check for reserved names
            for n in special:
                try:
                    raise ValueError('The attribute name "{}" is reserved.'.format(kwargs[n]))
                except KeyError:
                    continue
        # no special names
        except AttributeError:
            pass
            
class FormatGroupMeta(SpecialAttrsMeta):
    '''A metaclass that produces classes defining lines composed of  
    formatting members with optional line prefixes and separators between members.
    
    Formatter type must provide a static args_parse() method with a signature of: 
    
        args, kwargs = FormatterType.args_parse(*args)
        f = FormatterType(*args, **kwargs)
    
    Usage:
    
        class LineDef(metaclass=FormatGroupMeta):
            _formatter_type = CustomStaticFormatter
            _prefix = 'my prefix'
            _sep = ', '
            a = '{: 5>s}', 'foo'
            b = '{: 10>f}', 0
            c = '{}'
    '''
    _special = '_prefix _sep _formatter_type _formatters'.split()
    def __init__(cls, name, bases, mapping):
        formatter_type = cls._formatter_type
        formatter_defs = {k:v for k,v in mapping.items() if not k.startswith('_') and not callable(v)}
        formatter_args = {}
        formatter_kwargs = {}
        # build the formatter args, kwargs using formatter_type.args_parse
        for k,args in formatter_defs.items():
            args = [args] if isinstance(args, str) else args
            formatter_args[k], formatter_kwargs[k] = formatter_type.args_parse(*args)
        formatters = (formatter_type(*formatter_args[k], **formatter_kwargs[k]) for k in formatter_defs)
        # pass each set of args and kwargs to the formatter type
        cls._formatters = {k:formatter for k,formatter in zip(formatter_defs,formatters)}
        # attempt to grab extra types dict from an existing compiler (assume all of them are identical)
        try:
            cls._extra_types = next(iter(cls._formatters.values()))._parser._extra_types
        # no existing compiler 
        except (AttributeError, StopIteration):
            pass
        cls.__init__(name,bases,mapping)
    def format(cls, *args, _asdict=True, _popmappings=True, **unified_namespace):
        '''Return a combined formatted string using joined formatter members.
        
        Mapping objects can represent individual member argslists/namespaces and the values 
        will be appended to the args of the member name matching the key.
        
        Additional keyword arguments are passed to all formatteras as a "universal namespace".
        
        _popmappings:
            If True any Mapping object at the end of the args list is a member namespace. It will
            be spun out as the args via the name of that member or method as a key.
        _asdict:
            If True any object in args list that includes an .asdict or ._asdict attribute will 
            be treated as a Mapping object via the name of that member or method as a key.'''
        # optionally remove any mappings from the args list
        if _popmappings:
            # the slice of args in which to look for mappings (end to beginning) 
            slc=slice(-1,None,-1)
            # spin out any Mapping (or optionally .asdict/._asdict) objects starting from the end of args
            args, kwargs_from_args = args_kwargs_from_args(args, slc=slc, asdict=_asdict, ignore_conflicts=True, terminate_on_failure=True)
        else:
            args, kwargs_from_args = args, {}
        # argslist to be passed to each formatter member on a per-member basis
        try:
            # use unpacking to disallow multiple argslists to same member name
            format_args = od(**kwargs_from_args, **od((k,a) for k,a in zip(cls._formatters, args)))
        except TypeError as exc:
            if 'multiple values for keyword argument' in str(exc):
                key_conflict = next(k for k,_ in zip(cls._formatters, args) if k in kwargs_from_args)
                raise TypeError('Multiple argument sets provided under member name: {}.'.format(key_conflict)) from None
            else:
                raise
        # convert any single namespace arguments to an args list
        format_args = od((k,(a if not isinstance(a,str) and hasattr(a, '__iter__') else [a])) for k,a in format_args.items())
        return cls._prefix + cls._sep.join(formatter.format(*format_args.get(member,[]), **unified_namespace) for member,formatter in cls._formatters.items())
    def unformat(cls, string, evaluate_result=True):
        '''Inverse of format. Match my format group to the string exactly.

        Return a parse.Result or parse.Match instance or None if there's no match.
        '''
        fmat_str = (cls._sep if cls._sep else '').join(member._format_str for member in cls)
        # try to get extra type from precompiled parser set at initialization
        try:
            extra_types = cls._extra_types
        # parser wasn't precompiled so just assume the default
        except AttributeError:
            extra_types = dict(s=str)
        print('fmat_str:\n', fmat_str, 'string:\n', string[len(cls._prefix):], sep='\n')
        result = parse.parse(fmat_str, string[len(cls._prefix):], extra_types, evaluate_result=evaluate_result)
        # replace default output tuple with namedtuple
        if result is not None and result.fixed:
            result.fixed=list(result.fixed)
            def is_positional_field(member_parse):
                return member_parse[1:3]!=(None,None) and (member_parse[1] == '' or parse.parse('{:d}',member_parse[1]) is not None or parse.parse('{:d}{}',member_parse[1]) is not None)
            fixed_counts=[len([member_parse for member_parse in member.parse(member._format_str) if is_positional_field(member_parse)]) for member in cls]
            results=[]
            for count in fixed_counts:
                r=[]
                for _ in range(count):
                    r.append(result.fixed.pop(0))
                results.append(r)
            NT=nt(cls.__name__+'Data', ' '.join(cls._formatters))
            result.fixed=NT(*(r if len(r)>1 else r[0] for r in results))
        return result
        
    def __iter__(cls):
        yield from cls._formatters.values()