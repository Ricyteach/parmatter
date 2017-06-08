'''Base class for custom parmatters. The `args_parse` method is provided
to be overridden in case it is more convenient to pass arguments in a 
manner different from the initializer signature (capability used in the
format_group module).'''

from ..parmatter import Parmatter

class ArgsParseMixin():
    '''Provides default arg parsing behavior.'''
    @staticmethod
    def args_parse(*args):
        return args, {}
        
class ParmatterBase(Parmatter, ArgsParseMixin):
    '''A modified parsing formatter with an args_parse method.
	Use to modify signature of arguments sent to initializer.'''
    pass