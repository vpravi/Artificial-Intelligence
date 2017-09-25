import copy
import itertools

def main():
    f1 = open("input.txt","r")
    QDict = {}
    CPTDict = {}
    List = []
    temp = 0
    flag = 0
    NofVariables = 1
    lines = f1.readlines()
    inputs = [elem.strip('\n') for elem in lines]
    l = len(inputs)
    for queries in inputs:
        temp+=1
        loq = len(queries)
        if queries[0] == 'P'and flag == 0 :
            Qflag = 'P'
            newquery = queries[2:loq-1]
            checkQ(newquery,temp,QDict,Qflag)  
            l-1                  
        if queries[0] == 'E' and queries[1] == 'U':
            Qflag = 'EU'
            newquery = queries[3:loq-1]
            checkQ(newquery,temp,QDict,Qflag)
            l-1
        if queries[0] == 'M' and queries[1] == 'E' and queries[2] == 'U':
            Qflag = 'MEU'
            newquery = queries[4:loq-1]
            checkQ(newquery,temp,QDict,Qflag)
            l-1
        if queries == '******' and flag == 0:
            flag+=1
            l-1
            continue
        if flag == 1 and '*' not in queries:
            if '|' in queries:
                val = queries.split(' | ')
                NameofNode = val[0]
                Parents = val[1].split(' ')
                List.append([NameofNode,Parents])
                l-1
            else:
                NameofNode = queries
                List.append([NameofNode])
                l-1
        if queries == '***' and flag == 1:
            CPTDict[NofVariables] = List
            List = []
            NofVariables+=1
            l-1
        if queries == '******' and flag == 1:
            CPTDict[NofVariables] = List
            List = []
            NofVariables+=1
            flag+=1
            l-1
            continue
        if flag == 2:
            if '|' in queries:
                val = queries.split(' | ')
                NameofNode = val[0]
                Parents = val[1].split(' ')
                List.append([NameofNode,Parents])
                l-1
            else:
                NameofNode = queries
                List.append([NameofNode])  
                l-1
        if l == 0:
            break
               
    CPTDict[NofVariables] = List
    
    #QDict has all the queries
    #CPTDict has all the tables and their probabilities in rough format as taken from input
    #BayesDict has the Bayes Net, key is the query variable , first value in list is parents, 
    #second value is CPTsubDict which has the conditional probabilities the True/False values 
    #are the keys and the values are corresponding probabilities
    
    BayesDict = {}
    for i in CPTDict.keys():
        List = []
        val = CPTDict.get(i)
        if len(val[0]) == 1:
            parents = [[]]
            BayesDict[val[0][0]] = parents
            rest = val[1:]
            for entry in rest:
                val1 = entry[0].split()
                temp = Boolval(val1)
                List.append(temp)
        elif len(val[0]) == 2:
            children = []
            parents = [val[0][1]]
            for parent in parents[0]:
                BayesDict[parent].append(val[0][0])
            BayesDict[val[0][0]] = parents
            rest = val[1:]
            for entry in rest:
                val1 = entry[0].split()
                temp = Boolval(val1)
                List.append(temp)
        d = makeCPTdict(List)
        BayesDict[val[0][0]].append(d)
    
    for key in BayesDict.keys():
        vals = BayesDict.get(key)
        if len(vals)>2:
            v = vals[0:2]
            children = vals[2:]
            BayesDict[key] = v[0],v[1],children
        if len(vals)<3:
            BayesDict[key].append([])    

    DecisionNetwork,dnodes = ConstructDecisionNetwork(BayesDict)
    Answers = getAnswers(QDict,BayesDict,DecisionNetwork,dnodes)
    f2 = open("output.txt","w")
    m = len(Answers.keys())
    for key in Answers.keys():
        ans = Answers.get(key)
        if type(ans) == tuple:   
            l = list(ans)
            y = flattens(l)
            op = ''
            for s in range(0, len(y)):
                if s == len(y) - 1:
                    op = op + str(y[s])
                else:
                    op = op + str(y[s]) + " "
            m-=1
            f2.write(op+"\n")     
        elif m == 1:
            final = str(ans)
            m-=1
            f2.write(final)  
        else:
            final = str(ans)
            m-=1
            f2.write(final+"\n")
    
def getQueries(val,types,List,Liste):
    X = val[1]
    e = val[2]
    for i in X:
        z = i.split('=')
        variable = z[0]
        if len(z) == 2:
            if z[1] =='+':
                vals = True
                List.append([variable,vals])
            elif z[1] =='-':
                vals = False
                List.append([variable,vals])
        elif len(z) == 1:
            List.append([variable,None])
    for j in e:
        z = j.split('=')
        variable = z[0]
        if len(z) == 2:
            if z[1] =='+':
                vals = True
                Liste[variable] = vals
            elif z[1] =='-':
                vals = False
                Liste[variable] = vals
        elif len(z) == 1:
            Liste[variable] = None
    return List,Liste
        
def getAnswers(QDict,BayesDict,DecisionNetwork,dnodes):  
    AnswerDict = {}
    for entry in QDict.keys():
        List = []
        Liste = {}
        val = QDict.get(entry)
        if val[0] == 'P' and 'utility' not in BayesDict.keys():
            List,Liste = getQueries(val,'P',List,Liste)
            ans = EvaluatePQueries(List,Liste,BayesDict)
            answer = round(ans,2)
            solution = format(answer,'.2f')
            AnswerDict[entry] = solution 
        elif val[0] == 'P':
            List,Liste = getQueries(val,'P',List,Liste)
            ans = EvaluatePQueries(List,Liste,DecisionNetwork)
            answer = round(ans,2)
            solution = format(answer,'.2f')
            AnswerDict[entry] = solution   
        elif val[0] == 'EU':
            flag = 0
            List,Liste = getQueries(val,'EU',List,Liste)
            ans = EvaluateEUQueries(List,Liste,DecisionNetwork,dnodes,flag)
            answer = int(round(ans))
            AnswerDict[entry] = answer 
        elif val[0] == 'MEU':
            flag = 1
            List,Liste = getQueries(val,'MEU',List,Liste)
            ans,slist = EvaluateMEUQueries(List,Liste,DecisionNetwork,dnodes,flag)
            answer = int(round(ans))
            AnswerDict[entry] = slist,answer
        
    return AnswerDict

def flattens(givenlist):
    temp = []
    for i in givenlist:
        if isinstance(i,list): temp.extend(flattens(i))
        else: temp.append(i)
    return temp   

def EvaluateMEUQueries(List,Liste,DecisionNetwork,dnodes,flag):
    
    X = []
    for i in List:
        for value in i:
            if value in dnodes:
                X.append(value)
    
    n = len(X)
    newList = list(itertools.product([False, True], repeat=n))
    N = []
    for j in newList:
        b = list(j)
        N.append([X,b])   
    
    Z = []
    for k in N:
        x = []
        for i in range(len(k[0])):
            x.append([k[0][i],k[1][i]])
        Z.append(x)
    
    symboldict = {}
    EUvalues = []
    for newX in Z:
        val,booleanval = EvaluateEUQueries(newX,Liste,DecisionNetwork,dnodes,flag)
        EUvalues.append(val)
        temp1 = makeDictfromList(booleanval)
        symboldict[val] = temp1
    answer = max(EUvalues)
    foundsymbol = []
    for key in symboldict.keys():
        if key == answer:
            value = symboldict.get(key)
            
            s = value.values()
            for m in s:
                if m == True:
                    foundsymbol.append('+')
                elif m == False:
                    foundsymbol.append('-')
    return answer,foundsymbol

def EvaluateEUQueries(List,Liste,DecisionNetwork,dnodes,flag):
    for child in DecisionNetwork.keys():
        if child == 'utility':
            value = DecisionNetwork.get(child)
            parents = value[0]
            Dict = value[1]
            for entry in List:
                parent = entry[0]
                bools = entry[1]
                Liste[parent] = bools
            newparents = [x for x in parents if x not in dnodes]
            n = len(newparents) 
            newList = list(itertools.product([False, True], repeat=n))
            N = []
            for i in newList:
                b = list(i)
                N.append([newparents,b])   
            Z = []
            for X in N:
                x = []
                for i in range(len(X[0])):
                    x.append([X[0][i],X[1][i]])
                Z.append(x)
            Pvalues = []
            utilkey = []
            d = []
            for pt in range(len(parents)):
                for l in List:
                    if parents[pt] in l and parents[pt] in dnodes:
                        d.append([l[1],pt])
            for parent in parents:
                for newX in Z:
                    k = []
                    j = []
                    for i in range(len(newX)):
                        if parent in newX[i] and len(d) != 0:
                            bx = newX[i][1]
                            j.append(bx)
                            for w in d:
                                indexs = w[1]
                                j.insert(indexs,w[0])  
                            utilkey.append(tuple(j))
                        elif len(d) == 0 and len(parents) == 1:
                            bx = newX[i][1]
                            utilkey.append((bx,))
                        elif len(d) == 0 and len(parents) > 1:
                            bx = newX[i][1]
                            k.append(bx)
                    if k != []:
                        utilkey.append(tuple(k))
            for newXi in Z:
                val = EvaluatePQueries(newXi,Liste,DecisionNetwork)
                Pvalues.append(val)
            Sum = 0     
            for i in range(len(Pvalues)):
                item = Pvalues[i]*Dict.get(utilkey[i])
                Sum+=item
            symbols = copy.deepcopy(List)
    if flag == 0:
        return Sum
    elif flag == 1:
        return Sum,symbols

def EvaluatePQueries(List,Liste,BayesDict):    
    #p(B, E | A)= p(B, E, A) / p(A)   
    X = []
    E = []
    for i in List:
        X.append(i)
    for i in Liste.keys():
        X.append([i,Liste.get(i)])
    Products = []
    for i in range(len(X)):
        x = X[i]
        b = X[i+1:]
        e = makeDictfromList(b)
        if len(b) >= len(Liste):
            val = eliminationAsk(x[0],e,BayesDict)
            
            p = val.get(x[1])
            Products.append(p)
    z1 = findProduct(Products)
    answer1 = z1
    for i in Liste.keys():
        E.append([i,Liste.get(i)])
    Productz = []
    for i in range(len(E)):
        x = E[i]
        b = E[i+1:]
        e = makeDictfromList(b)
        if len(b) >= len(Liste):
            val = eliminationAsk(x[0],e,BayesDict)
            p = val.get(x[1])
            Productz.append(p)
    z2 = findProduct(Productz)
    answer2 = z2
    Final = answer1/answer2
    return Final
                           
def makeDictfromList(List):
    Dict = {}
    for i in List:
        Dict[i[0]] = i[1]
    return Dict

def findProduct(List):
    k = 1
    for i in List:
        k*=i
    return k
        
def makeCPTdict(entry):
    CPTsubDict = {}
    for tuples in entry:
        key = []
        for i in range(len(tuples)):
            if tuples[i] == True or tuples[i] == False:
                boolval = tuples[i]
                key.append(boolval)   
            elif tuples[i] == 'decision':
                value = 'decision'
            else:
                value = float(tuples[i])
        if key == []:
            key = None
            CPTsubDict[key] = value   
        else:
            val = tuple(key)
            CPTsubDict[val] = value
    return CPTsubDict
    
def Boolval(val1):
    for ch in range(len(val1)):
        if val1[ch] == '+':
            val1[ch] = True
        elif val1[ch] == '-':
            val1[ch] = False
    return val1
        
def checkQ(newquery,temp,QDict,Qflag):
    nq = ''.join(newquery.split())
    if '|' in nq:
        
        val=nq.split('|')
        QA = val[0].split(',')
        QB = val[1].split(',')
        QDict[temp] = Qflag,QA,QB
    else:
        QA = nq.split(',')
        QDict[temp] = Qflag,QA,[]
        
def eliminationAsk(X,e,BayesDict):

    eliminated = set()
    factors = []
    while len(eliminated) < len(BayesDict):
        factorvars = {}
        varss = []
        for var in list(BayesDict.keys()):
            if var not in eliminated:
                varss.append(var)
        varss = filter(lambda l: all(children in eliminated for children in BayesDict[l][2]), varss)
        for v in varss:
            factorvars[v] = [parent for parent in BayesDict[v][0] if parent not in e ]
            if v not in e: 
                factorvars[v].append(v)
        newvar = sorted(factorvars.keys(),key=(lambda x: (len(factorvars[x]), x)))[0]
        if len(factorvars[newvar]) > 0:
                ftuple = makefactor(newvar,factorvars,e,BayesDict)
                factors.append(ftuple)
        if newvar != X and newvar not in e:
                factors = sumout(newvar,factors)
        eliminated.add(newvar)   
 
    if len(factors) >= 2:
            tables = factors[0]
            for factor in factors[1:]:
                tables = pointwise(newvar,tables,factor)
        
    else:
        tables = factors[0]
        
    QueriesX = {False:tables[1][(False,)],True:tables[1][(True,)]}
    return normalize(QueriesX)
        
def makefactor(var,factorvars,e,BayesDict):
    variablelist = factorvars[var]
    parents = copy.deepcopy(BayesDict[var][0])
    parents.append(var)
    n = len(parents)
    newList2 = list(itertools.product([True,False], repeat=n))
    subanswers = {}
    Combinations = {}
    for j in newList2:
        condition = False
        for tuples in ((parents[i], j[i]) for i in range(min(len(parents), len(j)))):
            if tuples[0] in e and e[tuples[0]] != tuples[1]:
                condition = True
                break
            key = tuples[0]
            value = tuples[1]
            Combinations[key] = value
        if condition:
            continue
    
        k = []
        for v in variablelist:
            k.append(Combinations[v])
        key1 = tuple(k)
        value1 = Combinations[var]
        probability = Probability(var,value1,Combinations,BayesDict)
        subanswers[key1] = probability

    return (variablelist,subanswers)

def pointwise(var, factor1, factor2):

    mergevariables = factor1[0]+factor2[0]
    newvariables = list(set(mergevariables))
    n = len(newvariables)
    newList3 = list(itertools.product([True,False], repeat=n))
    newtable = {}
    Combinations = {}
    for k in newList3:
        for tuples in ((newvariables[i], k[i]) for i in xrange(min(len(newvariables), len(k)))):
            key = tuples[0]
            value = tuples[1]
            Combinations[key] = value
        k1 = []
        for v1 in newvariables:
            k1.append(Combinations[v1])
        key1 = tuple(k1)
        k2 = []
        for v2 in factor1[0]:
            k2.append(Combinations[v2])
        key2 = tuple(k2)
        k3 = []
        for v3 in factor2[0]:
            k3.append(Combinations[v3])
        key3 = tuple(k3)
        probability = factor1[1][key2] * factor2[1][key3]
        newtable[key1] = probability
        
    return (newvariables, newtable)

def sumout(var, factors):
    
    pointwisefactors = []  
    indexes = []
    for i in range(len(factors)):
        if var in factors[i][0]:
            pointwisefactors.append(factors[i])
            indexes.append(i)
    if len(pointwisefactors) > 1:
        for j in indexes[::-1]:
            del factors[j]
        answer = pointwisefactors[0]
        for pwfactor in pointwisefactors[1:]:
            answer = pointwise(var,answer, pwfactor)
        factors.append(answer)
    
    for i, factor in enumerate(factors):
        for j, v in enumerate(factor[0]):
            if v == var:
                newvariables = factor[0][:j] + factor[0][j+1:]
                newsubanswers = {}
                for e1 in factor[1]:
                    E = list(e1)
                    entry = tuple(E[:j] + E[j+1:])
                    E[j] = True
                    prob1 = factor[1][tuple(E)]
                    E[j] = False
                    prob2 = factor[1][tuple(E)]
                    Sum = prob1 + prob2
                    newsubanswers[entry] = Sum
                factors[i] = (newvariables, newsubanswers)
                if len(newvariables) == 0:
                        del factors[i]
    return factors

def normalize(QueriesX):
    total = 0.0
    for val in QueriesX.values():
        total += val
    for key in QueriesX.keys():
        QueriesX[key] /= total
    return QueriesX

def Probability(var, val, e, BayesDict):
    parents = BayesDict[var][0]
    if len(parents) == 0:
        tProbability = BayesDict[var][1][None]
    else:
        parentVals = [e[parent] for parent in parents]
        tProbability = BayesDict[var][1][tuple(parentVals)]
    if val==True: return tProbability
    else: return 1.0-tProbability

def ConstructDecisionNetwork(BayesNet):
    List = []
    bn = copy.deepcopy(BayesNet)
    for i in bn.keys():
        val = bn.get(i)
        if val[0] == []:
            tempCPTsubdict = val[1]
            for key in tempCPTsubdict.keys():
                if tempCPTsubdict.get(key) == 'decision':
                    del bn[i]
                    List.append(i)
    return bn,List

main() 