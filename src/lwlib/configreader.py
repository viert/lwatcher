#!/usr/bin/env python

from pyparsing import *

class ConfigReader(object):
  def __init__(self, filename):
    f = open(filename)
    self.rawconfig = f.read()
    f.close()
  
  def parse(self):
    
    EOL = Suppress(LineEnd())
    
    Comment = ('#' + SkipTo("\n"))
    
    ConfigOptionString = (Word(alphas) + '=' + Word(alphas+'/.,') + Optional(Comment) + LineEnd()).setResultsName('optionString', listAllMatches=True)
    ConfigDeclaration = (Keyword("[config]") + EOL + OneOreMore(ConfigOptionString) + Keyword("[/config]") + EOL).setResultsName("Config")
    
    ParserDirectiveArgumentList = delimitedList(QuotedString("'\""))
    ParserDirective = (Keyword("upTo") ^ Keyword("skip") ^ Keyword("skipTo") ^ Keyword("index")) + Suppress("(") + ParserDirectiveArgumentList + Suppress(")") + Optional(Comment) + LineEnd()
    ParserDeclaration = (Keyword("[parser]") + EOL + OneOrMore(ParserDirective) + Keyword("[/parser]") + EOL).setResultsName("Parser")
    
    
    