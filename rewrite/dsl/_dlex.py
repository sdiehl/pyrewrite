# _dlex.py. This file automatically created by PLY (version 3.4). Don't edit!
_tabversion   = '3.4'
_lextokens    = {'NAME': 1, 'INT': 1, 'DOUBLE': 1, 'ARROW': 1, 'COMB': 1, 'STRING': 1}
_lexreflags   = 0
_lexliterals  = ';,|:=(){}[]'
_lexstateinfo = {'INITIAL': 'inclusive'}
_lexstatere   = {'INITIAL': [('(?P<t_NEWLINE>\\n)|(?P<t_DOUBLE>\\d+\\.(\\d+)?)|(?P<t_INT>\\d+)|(?P<t_ARROW>->)|(?P<t_STRING>"([^"\\\\]|\\\\.)*")|(?P<t_NAME>[a-zA-Z_][a-zA-Z0-9_]*)|(?P<t_COMB>fail|id|\\<\\+|\\;)', [None, ('t_NEWLINE', 'NEWLINE'), ('t_DOUBLE', 'DOUBLE'), None, ('t_INT', 'INT'), ('t_ARROW', 'ARROW'), ('t_STRING', 'STRING'), None, (None, 'NAME'), (None, 'COMB')])]}
_lexstateignore = {'INITIAL': ' \t\n\r'}
_lexstateerrorf = {'INITIAL': 't_error'}
