import random

def main():
    f2 = open("output.txt","w")
    if getInput() == False:
        f2.write("no")
    else:
        NofGuests, NofTables,RMatrix = getInput()
        Clauses = Construct_Clauses(NofGuests,NofTables,RMatrix)
        value = dpll_satisfiable(Clauses)
        if value == False:
            f2.write("no")
        elif value == True:
            f2.write("yes"+"\n")
            SolutionModel = WalkSAT(Clauses,0.5,1000,NofGuests,NofTables)
            for i in range(1,NofGuests+1):
                for j in range(1,NofTables+1):
                    if SolutionModel[i][j] == True:
                        f2.write(str(i)+" "+str(j)+"\n")
                
def getInput():
    f1 = open("input.txt", "r")
    details = f1.readline().strip().split(' ')
    NofGuests = int(details[0])
    NofTables = int(details[1])
    
    if NofGuests == 0 or NofTables == 0:
        return False
    constraint_given = []
    for line in f1.readlines():
        constraint_given.append(line.strip().split(' '))
        
    RMatrix = [[0 for col in range(0,NofGuests+1)] for row in range(0,NofGuests+1)]
    for list in constraint_given:
        if list[0] == '':
            break
        else:
            i=int(list[0])
            j=int(list[1])
            if i <= NofGuests and j <= NofGuests and RMatrix[i][j] == 0:
                if list[2] == 'F':
                    RMatrix[i][j]=1
                elif list[2] == 'E':
                    RMatrix[i][j]=-1
            else:
                return False
                   
    return NofGuests,NofTables,RMatrix

def Construct_Clauses(NofGuests,NofTables,RMatrix):
    Clauses = [] 
    for i in range(1,NofTables+1):
        for j in range(i+1,NofTables+1):
            for k in range(1,NofGuests+1):
                Clauses.append('~'+'X'+str(k)+','+str(j)+'v'+'~'+'X'+str(k)+','+str(i))

    temp = []  
    for i in range(1,NofGuests+1):      
        for j in range(1,NofTables+1):
            temp.append('X'+str(i)+','+str(j))
        temp2 ='v'.join(temp)
        temp = []
        Clauses.append(temp2)
        
    for m in range(1,len(RMatrix)):
        for n in range(1,len(RMatrix)):  
            if RMatrix[m][n] == 1:
                for h in range(1,NofTables+1):
                    for l in range(1,NofTables+1):
                        if h!=l:
                            Clauses.append('~'+'X'+str(m)+','+str(h)+'v'+'~'+'X'+str(n)+','+str(l))
            elif RMatrix[m][n] == -1:
                for k in range(1,NofTables+1):
                    if NofTables == 1:
                        Clauses.append('~'+'X'+str(m)+','+'1'+'v'+'~'+'X'+str(n)+','+'1')
                    else:
                        Clauses.append('~'+'X'+str(m)+','+str(k)+'v'+'~'+'X'+str(n)+','+str(k))
    
    return Clauses
    
def CheckModelDict(Clause,Mod = {}):
    flag = 0
    Val1 = Clause.split('v')
    for value in Val1:
        if Mod.get(value) == True:
            return True
        elif Mod.get(value) == False:
            flag+=1   
        elif '~' in value:
            temp = value[1:]
            if temp in Mod:
                if Mod.get(temp) == False:
                    return True
                elif Mod.get(temp) == True:
                    flag+=1
    if flag == len(Val1):
        return False
    else:
        return None
    
def dpll_satisfiable(Clauses):
    temp = []
    for element in Clauses:   
        temp.append(element.split('v'))
    temp2 = flattens(temp)    
    flat = list(set(temp2))
    Symbols = []
    for i in flat:
        if '~' not in i:
            Symbols.append(i)       
    return dpll(Clauses,Symbols,{})
    

def dpll(Clauses,Symbols,Mod):
    unknown_clauses = []
    for c in Clauses:
        bool = CheckModelDict(c,Mod)
        if bool == False:
            return False
        if bool != True:
            unknown_clauses.append(c)
    if not unknown_clauses:
        return True
    P,value = find_puresymbol(Symbols,unknown_clauses) 
    if P:
        return dpll(Clauses,remove(Symbols,P),union(Mod,P,value))
    P,value = find_unitclause(unknown_clauses,Mod)
    if P:
        return dpll(Clauses,remove(Symbols,P),union(Mod,P,value))
    P = Symbols.pop()
    return((dpll(Clauses, Symbols, union(Mod, P, True)) or
            dpll(Clauses, Symbols, union(Mod, P, False))))
    
def union(Mod,P,value):
    tempmodel = Mod.copy()
    tempmodel[P] = value
    return tempmodel

def remove(Symbols,P):
    return [value for value in Symbols if value != P]
    
def find_puresymbol(Symbols,unknown_clauses):
    for s in Symbols:
        found_pos,found_neg = False,False
        for c in unknown_clauses:
            if not found_neg and '~'+s in c:
                found_neg = True
            if not found_pos and s in c:
                found_pos = True
        if found_pos != found_neg: 
            return s,found_pos
    return None,None
                    
def find_unitclause(Clauses,Mod):
    for c in Clauses:
        number = 0
        Val1 = c.split('v')
        for element in Val1:
            if '~' in element:
                sym = element[1:]   
                bool = False
            else:
                sym = element
                bool = True
            if sym not in Mod:
                number+=1
                P,value = sym,bool
        if number == 1:
            return P,value
    return None,None

def flattens(givenlist):
    temp = []
    for i in givenlist:
        if isinstance(i,list): temp.extend(flattens(i))
        else: temp.append(i)
    return temp   

def WalkSAT(Clauses,p,maxflips,NofGuests,NofTables):   
    model = [[random.choice([True,False]) for col in range(0,NofTables+1)] for row in range(0,NofGuests+1)]
    for i in range(maxflips):
        Satisfiable,val = CheckModel(Clauses,model)
        if Satisfiable == True:
            return model
            break
        clause = randomlySelectFalseClause(Clauses,model)
        if random.random() < p:
            symbol = randomlySelectSymbolFromClause(clause)
            model = flip(symbol,model)
        else:
            model = flipSymbolInClausesMaximizesNumberSatisfiedClauses(clause,Clauses,model)
    
                    
def randomlySelectFalseClause(Clauses,model):
    checkElement = []
    while True:
        listElement = []
        randomElement = random.choice(Clauses)
        if randomElement in checkElement:
            continue
        else:
            checkElement.append(randomElement)
        listElement.append(randomElement)
        clause,temp = CheckModel(listElement,model)
        if clause == False:
            return listElement
        if len(checkElement) == len(Clauses):
            break

def flip(element,model):   
    if '~' in element:
        temp = element[2:]
        indexes = temp.split(',')
        a = int(indexes[0])
        b = int(indexes[1])
        if model[a][b] == True:
            model[a][b] = False
        else:
            model[a][b] = True
    else:
        temp = element[1:]
        indexes = temp.split(',')
        a = int(indexes[0])
        b = int(indexes[1])
        if model[a][b] == True:
            model[a][b] = False
        else:
            model[a][b] = True      
    return model    
    
def randomlySelectSymbolFromClause(clause):
    Symbols = []
    Symbols = clause[0].split('v')
    element = random.choice(Symbols)
    return element

  
def flipSymbolInClausesMaximizesNumberSatisfiedClauses(clause,Clauses,model):
    Symbols = []
    Symbols = clause[0].split('v')
    maxsatisfied = -1
    for element in Symbols:
        tempModel = []
        tempModel = flip(element,model)
        value,numberofsatisfied = CheckModel(Clauses,tempModel)
        if value == True and numberofsatisfied == len(Clauses):
            return tempModel
        elif numberofsatisfied > maxsatisfied:
            maxsatisfied = numberofsatisfied
            maximizingsymbol = element
 
    maxmodel = flip(maximizingsymbol,model)
    return maxmodel
        
        
def CheckModel(Clauses,model):
    flag = 0
    add = 0
    for element in Clauses:
        Val1 = element.split('v')
        for value in Val1:
            flag = 0
            if '~' in value:
                temp = value[2:]
                indexes = temp.split(',')
                a = int(indexes[0])
                b = int(indexes[1])
                boolval = not model[a][b]
            else:
                temp = value[1:]
                indexes = temp.split(',')
                a = int(indexes[0])
                b = int(indexes[1])
                boolval = model[a][b]
            if boolval == True:
                add+=1
                flag = 1
                break
        if flag == 0:
            return False,add   
    return True,add



main()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
     
