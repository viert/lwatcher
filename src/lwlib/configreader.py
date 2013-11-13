#!/usr/bin/env python

from pyparsing import *

class ConfigReader(object):
    
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
  
  def __init__(self, filename):
    self.configfilename = filename
    self.config = {}
    self.config['options'] = {}
    self.config['vars'] = {}
    self.config['parser'] = []
    self.__parse()
  
  def __unescape(self, string):
    return string.replace("\\n", "\n").replace("\\t", "\t")
  
  def __parse(self):
    raw = ConfigReader.COLLECTOR_DECLARATION.parseFile(self.configfilename).asDict()

    for option in raw['config']['options']:
      self.config['options'][option[0]] = option[1]

    for var in raw['varsSection']['vars']:
      varName = var[0]
      funcName = var[1]
      args = var[2:]
      self.config['vars'][varName] = [funcName] + args

    for directive in raw['parser']['directives']:
      directive = [self.__unescape(x) for x in directive]
      self.config['parser'].append(directive)
      
# testing
if __name__ == '__main__':
  cr = ConfigReader("../conf/example.conf")
  print repr(cr.config)
    
    
    
    