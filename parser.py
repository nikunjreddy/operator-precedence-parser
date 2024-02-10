precedence = {}
assoc = {}
rhsidentifiers = []
production = {}
usedopt = []

def Isnonterminal(a):
    if 'A' <= a <= 'Z':
        return 1
    else:
        return 0

def Notnull(a):
    if a != "^":
        return 1
    else:
        return 0

def Isoperator(a):
    if not (a.isalpha() or a.isdigit()):
        return 1
    else:
        return 0

def Isunaryopt(a):
    if a == '!' or a == '~':
        return 1
    else:
        return 0

def convert(exp):
    l = len(exp)
    exp1 = list(exp)
    for i in range(l):
        if exp1[i].isalpha() or exp1[i].isdigit():
            exp1[i] = 'i'
    exp = ''.join(exp1)
    return exp

opl = []

# Scanning opprec.txt file and fixing precedence and assoc of operators
with open("opprec.txt", "r") as fp1:
    for line in fp1:
        opl = line.strip().split()
        if len(opl) < 3:
            print('Error: Incorrect format in precedence file')
            continue
        if not (Isoperator(opl[0]) or opl[1].isdigit() or (opl[2] == 'R' or opl[2] == 'L')):
            print('Error in precedence file')
            continue
        usedopt.append(opl[0])
        precedence[opl[0]] = int(opl[1])
        assoc[opl[0]] = opl[2]

usedopt.append('i')
usedopt.append('$')
usedopt = list(set(usedopt))

# Read and parse the grammar rules from f.txt
with open("f.txt", "r") as fp:
    for line in fp:
        line = line.strip()
        if not line:
            continue

        if '->' not in line:
            print(f'Error :: -> should be present in production: {line}')
            exit(0)

        a, b = line.split('->')
        a = a.strip()
        b = b.strip()

        if Isnonterminal(a):
            if Notnull(b):
                if len(b) == 1:
                    if Isnonterminal(b) or b == 'i':
                        rhsidentifiers.append(b)
                    else:
                        print(f'Error :: in Production: {line}')
                        exit(0)
                elif len(b) == 2:
                    if Isoperator(b[0]) and Isnonterminal(b[1]):
                        if not b[0] in usedopt:
                            print(f'Error in production: {line}')
                            exit(0)
                    else:
                        print(f'Error :: in Production: {line}')
                        exit(0)
                elif len(b) == 3:
                    if b[0] == '(' and b[1].isalpha() and b[2] == ')':
                        usedopt.append(b[0])
                        usedopt.append(b[2])
                    elif b[0].isalpha() and Isoperator(b[1]) and b[2].isalpha():
                        if not b[1] in usedopt:
                            print(f'Error in production: {line}')
                            exit(0)
                    else:
                        print(f'Error :: Production is incorrect: {line}')
                        exit(0)
                if b in production.keys():
                    print(f'Error :: NO same RHS is allowed for alternative LHS: {line}')
                    exit(0)
                else:
                    production[b] = a
            else:
                print(f'Error :: Null in production: {line}')
                exit(0)
        else:
            print(f'Error :: LHS should be Non-Terminal in production: {line}')
            exit(0)

# Creating the parser table
ptable = {}
for j in range(len(usedopt)):
    temp = {}
    for i in range(len(usedopt)):
        if usedopt[i] == '$' and usedopt[j] == '$':
            temp['$'] = 'accept'
        elif usedopt[i] == 'i' and usedopt[j] == 'i':
            temp['i'] = 'nd'
        elif usedopt[i] == '(' and Isoperator(usedopt[j]):
            temp['('] = 's'
        elif usedopt[i] == ')' and Isoperator(usedopt[j]) and usedopt[j] != '(':
            temp[')'] = 'r'
        elif precedence.get(usedopt[i], 0) > precedence.get(usedopt[j], 0):
            temp[usedopt[i]] = 's'
        elif precedence.get(usedopt[i], 0) < precedence.get(usedopt[j], 0):
            temp[usedopt[i]] = 'r'
        else:
            if assoc.get(usedopt[i], 'R') == 'R':
                temp[usedopt[i]] = 's'
            else:
                temp[usedopt[i]] = 'r'
    ptable[usedopt[j]] = temp

# Processing or parsing user input for a single expression
exp = input('Enter expression: ')
exp = exp.strip()
exp = convert(exp)
exp += '$'
stk = "$"
i = 0
print('\tStack\t\tExp\t\tAction\t')
print('\t', stk, '\t\t', exp, '\t\t')

while i < len(exp):
    l = len(stk)
    j = l - 1
    if Isnonterminal(stk[j]):
        j = j - 1
    t = stk[j]
    t2 = exp[i]

    if Isnonterminal(t):
        print('Error :: There should be an operator between two terminals.')
        break

    if t2 not in usedopt:
        print('Wrong operator is used')
        break

    if ptable[t][t2] == 'r':
        if t == 'i':
            var1 = production[stk[j]]
            stk = stk[:-1]
            stk += var1
        elif j < l - 1 and stk[j + 1] in rhsidentifiers:
            var1 = production[stk[j + 1]]
            stk = stk[:-1]
            stk += var1
        elif j < l - 1 and Isunaryopt(stk[j]) and (stk[j + 1] in rhsidentifiers or stk[j + 1] == 'E') and stk[l - 2:] in production:
            var1 = production[stk[l - 2:]]
            stk = stk[:-2]
            stk += var1
        elif j < l - 1 and l >= 3 and Isoperator(stk[j]) and (stk[j + 1] in rhsidentifiers or stk[j + 1] == 'E') and (
                stk[j + 1] in rhsidentifiers or stk[j + 1] == 'E') and stk[l - 3:] in production:
            var1 = production[stk[l - 3:]]
            stk = stk[:-3]
            stk += var1
        elif t == ')':
            if l >= 3 and (stk[l - 2] in rhsidentifiers or stk[l - 2] == 'E') and stk[l - 3] == '(':
                if stk[l - 3:] not in production:
                    print('Error:: not present in production')
                    break
                var1 = production[stk[l - 3:]]
                stk = stk[:-3]
                stk += var1
        else:
            print('Error-----------')
            break
        print('\t', stk, '\t\t', exp[i:], '\t\tReduced')
    elif ptable[t][t2] == 's':
        stk += exp[i]
        i += 1
        print('\t', stk, '\t\t', exp[i:], '\t\tShifted')
    elif ptable[t][t2] == 'nd':
        print('Error :: not a correct expression corresponding to the production')
        break
    elif ptable[t][t2] == 'accept':
        print('\nBravo :: Expression is correct!')
        break
    else:
        print('Error')
        break
