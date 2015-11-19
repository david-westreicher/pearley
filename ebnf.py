import sys
import string
from pearley import *

'''
    SingleTerm(',',True)]),
    SingleTerm('operation',False)]),
Production('operation',[SingleTerm('r',True),SingleTerm('e',True),SingleTerm('d',True)]),
Production('operation',[SingleTerm('e',True),SingleTerm('x',True),SingleTerm('t',True)]),
Production('operation',[SingleTerm('i',True),SingleTerm('g',True),SingleTerm('n',True)]),
'''

def getebnfgrammar():
    productions = [
        Production('ebnf',[
            SingleTerm('term',False),
            SingleTerm('blanks',False),
            SingleTerm('=',True),
            SingleTerm('blanks',False),
            SingleTerm('orlist',False)]),
        Production('orlist',[SingleTerm('termlist',False)],'red'),
        Production('orlist',[
            SingleTerm('orlist',False),
            SingleTerm('blanks',False),
            SingleTerm('|',True),
            SingleTerm('blanks',False),
            SingleTerm('termlist',False)],'red'),
        Production('termlist',[SingleTerm('term',False)],'red'),
        Production('termlist',[
            SingleTerm('termlist',False),
            SingleTerm('blanks',False),
            SingleTerm('term',False)],'red'),
        Production('term',[SingleTerm('realterm',False)]),
        Production('term',[SingleTerm('variable',False)]),
        Production('realterm',[
            SingleTerm('"',True),
            SingleTerm('string',False),
            SingleTerm('"',True)],'ext'),
        Production('blanks',[SingleTerm(' ',True)],'ign'),
        Production('blanks',[SingleTerm('blanks',False),SingleTerm(' ',True)],'ign'),
        Production('variable',[SingleTerm('letter',False)],'red'),
        Production('variable',[SingleTerm('variable',False),SingleTerm('letter',False)],'red'),
        Production('string',[SingleTerm('printable',False)],'red'),
        Production('string',[SingleTerm('string',False),SingleTerm('printable',False)],'red'),
    ]
    for char in string.ascii_lowercase: 
        productions.append(Production('letter',[SingleTerm(char,True)]))
    for char in string.printable[:-5]: 
        # guarantees nonambiguity of grammar:)
        if char=='"':continue
        productions.append(Production('printable',[SingleTerm(char,True)]))
    return productions

def reducetree(tree):
    # seems to be a terminal
    if tree.rule is None:
        return [tree]
    op = tree.rule.op
    result = []
    if op is None:
        newchildren = []
        result.append(Tree(tree.name,tree.rule,newchildren))
        for child in tree.children:
            newchildren.extend(reducetree(child))
    else:
        if op=='ign':
            pass
        if op=='ext':
            for i,child in enumerate(tree.children):
                if not tree.rule.terms[i].isterm:
                    result.extend(reducetree(child))
        if op=='red':
            for child in tree.children:
                result.extend(reducetree(child))
    return result

grammar = getebnfgrammar()
#for prod in grammar:
    #print('\t'+str(prod))

def treetoterm(tree):
    typ = tree.rule.terms[-1].name
    isterm = typ=='realterm'
    if isterm:
        res = []
        for child in tree.children:
            name=child.children[0].name
            res.append(SingleTerm(name,isterm))
        return res
    else:
        name = ''
        for child in tree.children:
            name+=child.children[0].name
        return [SingleTerm(name,isterm)]

def treetoprod(tree):
    prods = [] 
    name = None
    for child in tree.children:
        if child.rule is not None:
            name = treetoterm(child)[0].name
        else:
            break
    terms = []
    for child in tree.children[2:]:
        if child.rule is not None:
            for t in treetoterm(child):
                terms.append(t)
        else:
            prods.append(Production(name,terms))
            terms = []
    prods.append(Production(name,terms))
    return prods

parsedgrammar = []
def parse(txt,grammar,isebnf=False):
    statespace = earley(grammar,txt)
    if statespace is not None:
        #printspace(statespace,txt)
        #print('%s is a valid sentence' % txt)
        tree = parsetree(grammar,statespace,txt)
        tree = reducetree(tree)[0]
        if isebnf:
            prods = treetoprod(tree)
            parsedgrammar.extend(prods)
        else:
            print(tree)

if len(sys.argv)>3:
    parse(sys.argv[1],grammar,True)
else:
    for line in open(sys.argv[1],'r'):
        line = line[:-1]
        parse(line,grammar,True)
print('PARSEDGRAMMAR')
for prod in parsedgrammar:
    print('\t'+str(prod))
parse(sys.argv[2],parsedgrammar)
