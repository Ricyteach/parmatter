'''parmatter
--------

Tools for parsable formatters (with unformat() capability).

Example usage: 

    >>> f = Parmatter()
    >>> assert f.format('{}', 'foo') = 'foo'
    >>> assert list(f.unformat('{}', 'foo')) = ['foo']
'''

import string
import parse as _parse # avoid potential name conflicts with parse methods

# NOTE: All the Formatter docstrings mostly copied from the string docs page (Formatter does not have 
# its own docstrings). 
class Formatter():
    '''Re-implementation of string.Formatter to add docstrings, and as a container so that the parse 
    method can be overridden for other purposes and child classes can still override other API methods 
    using super().'''
    # just one Formatter instance needed for all classes
    __formatter = string.Formatter()
    def __init__(self, *args, **kwargs):
        self.__formatter.__init__(*args, **kwargs)
    def format(self, format_string, *args, **kwargs):
        '''The primary API method. Takes a format string and injects an 
        arbitrary set of positional and keyword arguments using format string
        syntax. 
        
        Handle formmatting logic by overriding get_value, format_field,
        check_unused_args, and others per PEP 3101 and the docs.'''
        return self.__formatter.format(format_string, *args, **kwargs)
    def vformat(self, format_string, args, kwargs):
        '''This function does the actual work of formatting. It is exposed as a separate function for cases 
        where you want to pass in a predefined dictionary of arguments, rather than unpacking and repacking 
        the dictionary as individual arguments using the *args and **kwargs syntax. vformat() does the work 
        of breaking up the format string into character data and replacement fields. It calls the various 
        other methods used by the string formatting API.'''
        return self.__formatter.vformat(format_string, args, kwargs)
    def parse(self, format_string):
        '''Loop over the format_string and return an iterable of tuples (literal_text, field_name, format_spec, 
        conversion). This is used by vformat() to break the string into either literal text, or replacement 
        fields.
        
        The values in the tuple conceptually represent a span of literal text followed by a single replacement 
        field. If there is no literal text (which can happen if two replacement fields occur consecutively), 
        then literal_text will be a zero-length string. If there is no replacement field, then the values of 
        field_name, format_spec and conversion will be None.'''
        return self.__formatter.parse(format_string)
    def get_field(self, field_name, args, kwargs):
        '''Given field_name as returned by parse() (see above), convert it to an object to be formatted. 
        Returns a tuple (obj, used_key). The default version takes strings of the form defined in PEP 3101, 
        such as “0[name]” or “label.title”. args and kwargs are as passed in to vformat(). The return value 
        used_key has the same meaning as the key parameter to get_value().'''
        return self.__formatter.get_field(field_name, args, kwargs)
    def get_value(self, key, args, kwargs):
        '''Retrieve a given field value. The key argument will be either an integer or a string. 
        If it is an integer, it represents the index of the positional argument in args; if it 
        is a string, then it represents a named argument in kwargs.
        
        The args parameter is set to the list of positional arguments to vformat(), and the kwargs 
        parameter is set to the dictionary of keyword arguments.
        
        For compound field names, these functions are only called for the first component of the 
        field name; Subsequent components are handled through normal attribute and indexing operations.
        
        So for example, the field expression ‘0.name’ would cause get_value() to be called with a key 
        argument of 0. The name attribute will be looked up after get_value() returns by calling the 
        built-in getattr() function.
        
        If the index or keyword refers to an item that does not exist, then an IndexError or KeyError 
        should be raised.'''
        return self.__formatter.get_value(key, args, kwargs)
    def check_unused_args(self, used_args, args, kwargs):
        '''Implement checking for unused arguments if desired. The arguments to this function is the set 
        of all argument keys that were actually referred to in the format string (integers for positional 
        arguments, and strings for named arguments), and a reference to the args and kwargs that was passed 
        to vformat. The set of unused args can be calculated from these parameters. check_unused_args() is 
        assumed to raise an exception if the check fails.'''
        return self.__formatter.check_unused_args(used_args, args, kwargs)
    def format_field(self, value, format_spec):
        '''Simply calls the global format() built-in. Provided so that subclasses can override it.'''
        return self.__formatter.format_field(value, format_spec)
    def convert_field(self, value, conversion):
        '''Converts the value (returned by get_field()) given a conversion type (as in the tuple returned by 
        the parse() method). The default version understands ‘s’ (str), ‘r’ (repr) and ‘a’ (ascii) conversion 
        types.'''
        return self.__formatter.convert_field(value, conversion)

class Parmatter(Formatter):
    '''A parsable formatter. The various string format API methods can be overridden by child classes using 
    super() for convenience, except the Parmatter.parse method. It is routed to the parser, not the formatter. 
    If a child class needs to access __formatter.parse, it needs be done thusly:
        obj._Parmatter__formatter.parse'''
    def format(self, format_str, *args, **kwargs):
        '''Overridden to divert to any overridden string format API methods.'''
        return Formatter.format(self, format_str, *args, **kwargs)
    def vformat(self, format_str, args, kwargs):
        '''Overridden to divert to any overridden string format API methods.'''
        return Formatter.vformat(self, format_str, args, kwargs)
    def unformat(self, format, string, extra_types=dict(s=str), evaluate_result=True):
        return _parse.parse(format, string, extra_types, evaluate_result)
    unformat.__doc__ = _parse.Parser.parse.__doc__