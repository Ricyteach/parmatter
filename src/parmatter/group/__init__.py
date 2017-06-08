'''Parmatter groups are created in order to define different line types for files. 
An individual parmatter could also define a line type on its own, but the parmatter
group also has options for prefixes, separators, and naming of parmatters (useful
in formatting and unformatting).
'''
from .meta import FormatGroupMeta
from .factory import FormatGroup