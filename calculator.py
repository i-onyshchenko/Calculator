import lexscan
from math import pi, sin, cos, tan, log, sqrt, exp
from pprint import pprint

prec = {'^': 4, '*': 3, '/': 3, '+': 2, '-': 2}
assoc = {'^': 'right', '*': 'left', '/': 'left', '+': 'left', '-': 'left'}
constants = {'PI': pi}
operators = {'+': lambda x,y: x+y, '-': lambda x,y: x - y, '*': lambda x,y: x*y, '/': lambda x,y: x/y, '^': lambda x,y: x**y}
functions = {'sin': lambda x: sin(x), 'cos':  lambda x: cos(x),
             'tan': lambda x: tan(x), 'log': lambda x: log(x),
             'sqrt': lambda x: sqrt(x), 'exp': lambda x: exp(x)}


def getTokens(expression):
    spaceexp = lexscan.ScanExp(r'\s+', significant=False)
    wordexp = lexscan.ScanExp(r'[a-z]+', name="function")
    numexp = lexscan.ScanExp(r'\d+', name="number")
    leftPar = lexscan.ScanExp(r'\(', name="leftPar")
    rightPar = lexscan.ScanExp(r'\)', name="rightPar")
    operator = lexscan.ScanExp(r'[\+\-\*\/\^]', name="operator")
    return lexscan.tokenize(expression, (spaceexp, wordexp, numexp, leftPar, rightPar, operator))


def getRPN(tokens):
    res = []
    stack = []
    for tok in tokens:
        # some utils
        if tok.text in constants.keys():
            tok.text = constants[tok.text]
            tok.name = 'number'
        elif tok.text == 'x':
            tok.name = 'number'

        if tok.name == 'number':
            res.append(tok)
        elif tok.name == 'function':
            stack.append(tok)
        elif tok.name == 'operator':
            while len(stack) > 0 and (stack[-1].name == 'function' or (stack[-1].name == 'operator' and (prec[stack[-1].text] > prec[tok.text] or (prec[stack[-1].text] == prec[tok.text] and assoc[stack[-1].text] == 'left')))):
                res.append(stack.pop())
            stack.append(tok)
        elif tok.name == 'leftPar':
            stack.append(tok)
        elif tok.name == 'rightPar':
            while stack[-1].name != 'leftPar':
                res.append(stack.pop())
                if len(stack) == 0:
                    raise Exception("Mismatched parentheses")
            if stack[-1].name == 'leftPar':
                stack.pop()
        else:
            raise Exception("Invalid operation")

    while len(stack) > 0:
        top = stack.pop()
        if top.name == 'leftPar' or top.name == 'rightPar':
            raise Exception("Mismatched parentheses")
        res.append(top)

    return res


def getResult(tokens, x):
    stack = []
    for tok in tokens:
        if tok.name == 'function':
            stack.append(float(functions[tok.text](stack.pop())))
        elif tok.name == 'operator':
            op2 = stack.pop()
            op1 = stack.pop()
            stack.append(float(operators[tok.text](op1, op2)))
        else:
            # replace symbolic 'x' with value
            if tok.text == 'x':
                stack.append(x)
            else:
                stack.append(float(tok.text))

    return stack.pop()


if __name__ == "__main__":
    # expression = '2*sin(1/(exp(3*x)+2^3)-tan(x+PI/2))'
    expression = '2*sin(1/((exp(3*x)+2)^3)-(tan(x+PI/2) + 1))'
    print(getResult(getRPN(getTokens(expression)), 2))
