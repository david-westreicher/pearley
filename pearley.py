import sys
from collections import namedtuple

class SingleTerm(namedtuple('SingleTerm','name isterm')):
    __slots__ = ()
    def __repr__(self):
        return str(self)
    def __str__(self):
        if self.isterm:
            return '"'+self.name+'"'
        return self.name
class Production(namedtuple('Production','nonterm terms op')):
    __slots__ = ()
    def __new__(self,nonterm,terms,op=None):
        return super(Production,self).__new__(self,nonterm,terms,op)
    def __repr__(self):
        return str(self)
    def __str__(self):
        lhs = str(self.nonterm)+' -> '
        if len(self.terms)==1:
            return lhs+str(self.terms[0])
        return lhs+str(self.terms)
    def dotstr(self,dot):
        lhs = str(self.nonterm)+' -> '
        rhs = str(self.terms[0]) if len(self.terms)==1 else str(self.terms)
        if dot==0:
            return lhs+'*'+rhs
        if dot==len(self.terms):
            return lhs+rhs+'*'
        return lhs+str(self.terms[:dot])+'*'+str(self.terms[dot:])
class State(namedtuple('State','prod dot pos')):
    __slots__ = ()
    def __repr__(self):
        return str(self)
    def __str__(self):
        return self.prod.dotstr(self.dot).ljust(30)+'@'+str(self.pos)
    def complete(self):
        return self.dot==len(self.prod.terms)
    def nextterm(self):
        return self.prod.terms[self.dot]
    def __hash__(self):
        return hash(str(self))
class Tree(namedtuple('Tree','name rule children')):
    __slots__ = ()
    def __str__(self):
        return self.tostr(0)
    def tostr(self,depth):
        out = ((' '*depth*2) + str(self.name)).ljust(60)+str(self.rule)+'\n'
        for child in self.children:
            out += child.tostr(depth+1)
        return out
    def reverse(self):
        self.children.reverse()
        for child in self.children:
            child.reverse()
        return self

def earley(productions,sentence):
    productions.insert(0,Production('START',[SingleTerm(productions[0].nonterm,False)]))
    statespace = [set([(State(productions[0],0,0))])]
    queue = []
    def predictor(nonterm,k):
        for prod in productions:
            if prod.nonterm==nonterm.name:
                state = State(prod,0,k)
                if state not in statespace[k]:
                    queue.append((k,state))
    def scanner(char,k):
        for state in statespace[k]:
            if state.complete():continue
            term = state.nextterm()
            if term.isterm and term.name==char:
                queue.append((k+1,State(state.prod,state.dot+1,state.pos)))
    def completer(compstate,k):
        for state in statespace[compstate.pos]:
            if state.complete():continue
            term = state.nextterm()
            if not term.isterm and term.name==compstate.prod.nonterm:
                newstate = State(state.prod,state.dot+1,state.pos)
                if newstate not in statespace[k]:
                    queue.append((k,newstate))
    def solvequeue(k,char = None):
        queue.extend([(k,state) for state in statespace[k]])
        if char is not None: statespace.append(set())
        while len(queue)>0:
            i,state = queue.pop(0)
            statespace[i].add(state)
            if i!=k: continue
            if state.complete():
                completer(state,k)
            else:
                term = state.nextterm()
                if term.isterm:
                    scanner(char,k)
                else:
                    predictor(term,k)

    for k,char in enumerate(sentence):
        solvequeue(k,char)
    solvequeue(len(sentence))
    finalstate = State(productions[0],len(productions[0].terms),0)
    solved = finalstate in statespace[-1]
    del productions[0]
    if solved:
        # TODO remove all START rules from the statespace
        return statespace
    printspace(statespace,sentence)
    print('%s is not a valid sentence' % sentence)
    return None

def printspace(statespace,sentence):
    print('STATESPACE')
    for i,s in enumerate(statespace):
        print('S(%d), %s*%s'%(i,sentence[:i],sentence[i:]))
        for el in s:
            print('\t'+str(el))

def parsetree(grammar,statespace,sentence):
    reducedspace = []
    for statelist in statespace:
        newlist = []
        for state in statelist:
            if state.complete():
                newlist.append(state)
        reducedspace.append(newlist)
    printspace(reducedspace,sentence)
    for state in reducedspace[-1]:
        name = state.prod.nonterm 
        if name == grammar[0].nonterm and state.pos==0:
            start = Tree(name,state.prod,[])
            parsetreerec(start,state,reducedspace,len(reducedspace)-1)
            #printspace(reducedspace,sentence)
            return start.reverse()

def parsetreerec(start,remstate,reducedspace,index):
    reducedspace[index].remove(remstate)
    #printspace(reducedspace,'')
    for term in reversed(start.rule.terms):
        name = term.name
        if term.isterm:
            start.children.append(Tree(name,None,[]))
            continue
        for index in range(index,0,-1):
            state = None
            for s in reducedspace[index]:
                if name == s.prod.nonterm:
                    state = s
                    break
            if state is None: continue
            child = Tree(name,state.prod,[])
            # TODO this is too greedy, need to incorporate parse start
            parsetreerec(child,state,reducedspace,index)
            start.children.append(child)
            break
