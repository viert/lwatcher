#!/usr/bin/env python

from pyparsing import *

pd = """  [parser]
    # comment
    skipTo(' ')
    skip(' ')
    skipTo(' ')
    skip(' ')
    upTo(' ', 'time')
    index('time')
    skip(' ')
    upTo(' ', 'host')
    skip(' ')
    upTo(':', 'from')
    skip(':')
    skip(' ')
    upTo('\\n', 'message')
    skip('\\n')
    # indexing fields
    index('from')
  [/parser]
"""

cd = """  [config]
    name = example
    log = /var/log/syslog
    period = 300,15              # 285-315 seconds
  [/config]
"""

vd = """  [vars]
    # comment 1
    maxMessagesFrom = maxCount('from')
    someMax = max('some') # comment 2
  [/vars]
"""

comment_line = " # blah minor "
directive_line = " skipTo('a') # some comment "
sgl_quoted = "'abc'"
dbl_quoted = '"abc"'
quoted_args = "'sql', \"dql\""
braced_quoted_args = "('sql', \"dql\")"
directive_name = "skip"
directive = "skip(' ')\n"
commented_directive = "skipTo(' ') # comment is here\n"
directive_list = """    skip(' ')
    skipTo(' ')
    skip(' ')
    upTo(' ', 'time')
    # here is the comment and empty line after

    index('time')
"""
option = "period = 300,15"
commented_option = "log = /var/log/syslog # 285-315 seconds"
function = "maxCount('from')"
variable = "var1 = max('to')"


AVAILABLE_FUNCTIONS = ['max', 'maxCount']

EOL = Suppress("\n" ^ LineEnd())

COMMENT = Suppress("#" + SkipTo(EOL))
QUOTED_STRING = QuotedString("'") ^ QuotedString('"')
QUOTED_ARGUMENT_LIST = delimitedList(QUOTED_STRING)
ARGUMENT_LIST = delimitedList(QUOTED_STRING ^ Word(alphanums))
BRACED_QUOTED_ARGUMENT_LIST = Suppress("(") + QUOTED_ARGUMENT_LIST + Suppress(")")
BRACED_ARGUMENT_LIST = Suppress("(") + ARGUMENT_LIST + Suppress(")")

DIRECTIVE_NAME = (Keyword("skip") ^ Keyword("skipTo") ^ Keyword("upTo") ^ Keyword("fromTo") ^ Keyword("index"))
DIRECTIVE = (DIRECTIVE_NAME + BRACED_QUOTED_ARGUMENT_LIST + Optional(COMMENT)).setResultsName('directives', listAllMatches=True)
DIRECTIVE_LIST = OneOrMore(DIRECTIVE ^ COMMENT)
PARSER_DECLARATION = (Suppress(Keyword("[parser]")) + DIRECTIVE_LIST + Suppress(Keyword("[/parser]"))).setResultsName('parser')

OPTION = (Word(alphas) + Suppress('=') + Word(alphanums+'/.,') + Optional(COMMENT)).setResultsName('options', listAllMatches=True)
OPTION_LIST = OneOrMore(OPTION ^ COMMENT)
CONFIG_DECLARATION = (Suppress(Keyword("[config]")) + OPTION_LIST + Suppress(Keyword("[/config]"))).setResultsName('config')

VARIABLE_NAME = (Word(alphanums))
FUNCTION_NAME = (Or([Keyword(x) for x in AVAILABLE_FUNCTIONS]))
FUNCTION = (FUNCTION_NAME + BRACED_ARGUMENT_LIST)
VARIABLE_DECLARATION = (VARIABLE_NAME + Suppress('=') + FUNCTION).setResultsName('vars', listAllMatches=True)
VARIABLE_DECLARATION_LIST = OneOrMore(VARIABLE_DECLARATION ^ COMMENT)
VARS_DECLARATION = (Suppress(Keyword("[vars]")) + VARIABLE_DECLARATION_LIST + Suppress(Keyword("[/vars]"))).setResultsName('varsSection')

SECTION_LIST = CONFIG_DECLARATION & PARSER_DECLARATION & VARS_DECLARATION ^ COMMENT
COLLECTOR_DECLARATION = (Suppress(Keyword("[collector]")) + SECTION_LIST + Suppress(Keyword("[/collector]"))).setResultsName('collector')

print "testing comments"
print comment_line + " : " + repr(COMMENT.parseString(comment_line))
print comment_line + "\\n : " + repr(COMMENT.parseString(comment_line + "\n"))
print
print "testing quoted line"
print sgl_quoted + " : " + repr(QUOTED_STRING.parseString(sgl_quoted))
print dbl_quoted + " : " + repr(QUOTED_STRING.parseString(dbl_quoted))
print
print "testing quoted argument list"
print quoted_args + " : " + repr(QUOTED_ARGUMENT_LIST.parseString(quoted_args))
print braced_quoted_args + " : " + repr(BRACED_QUOTED_ARGUMENT_LIST.parseString(braced_quoted_args))
print
print "testing directive"
print directive_name + " : " + repr(DIRECTIVE_NAME.parseString(directive_name))
print directive.strip() + " : " + repr(DIRECTIVE.parseString(directive))
print commented_directive.strip() + " : " + repr(DIRECTIVE.parseString(commented_directive))
print 
print directive_list
print "^^^^^"
print repr(DIRECTIVE_LIST.parseString(directive_list).asDict())
print
print "testing parser declaration"
print repr(PARSER_DECLARATION.parseString(pd).asDict()['parser']['directives'])
print
print "testing config declaration"
print option + " : " + repr(OPTION.parseString(option))
print repr(CONFIG_DECLARATION.parseString(cd).asDict())
print
print "testing variables"
print function + " : " + repr(FUNCTION.parseString(function))
print variable + " : " + repr(VARIABLE_DECLARATION.parseString(variable).asDict())
print
print vd
print "^^^^^^^^"
print repr(VARS_DECLARATION.parseString(vd).asDict())
print
print "The Whole Config Test"
print
config = COLLECTOR_DECLARATION.parseFile("../conf/example.conf").asDict()
print repr(config.keys())
print "options: " + repr(config['config']['options'])
print "parser: " + repr(config['parser']['directives'])
print "vars: " + repr(config['varsSection'])
