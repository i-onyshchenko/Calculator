import lexscan
from math import pi, sin, cos, tan, log, sqrt, exp
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint


class Calculator:
    prec = {'^': 4, '*': 3, '/': 3, '+': 2, '-': 2}
    assoc = {'^': 'right', '*': 'left', '/': 'left', '+': 'left', '-': 'left'}
    constants = {'PI': pi}
    operators = {'+': lambda x, y: x+y, '-': lambda x, y: x - y, '*': lambda x, y: x*y, '/': lambda x, y: x/y, '^': lambda x, y: x**y}
    functions = {'sin': lambda x: sin(x), 'cos': lambda x: cos(x),
                 'tan': lambda x: tan(x), 'log': lambda x: log(x),
                 'sqrt': lambda x: sqrt(x), 'exp': lambda x: exp(x)}

    def __init__(self):
        self.expr = None
        self.tokens = None
        self.RPN = None
        self.a = None
        self.b = None

    @staticmethod
    def _getTokens(expr):
        spaceexp = lexscan.ScanExp(r'\s+', significant=False)
        wordexp = lexscan.ScanExp(r'[a-z]+', name="function")
        numexp = lexscan.ScanExp(r'\d+', name="number")
        leftPar = lexscan.ScanExp(r'\(', name="leftPar")
        rightPar = lexscan.ScanExp(r'\)', name="rightPar")
        operator = lexscan.ScanExp(r'[\+\-\*\/\^]', name="operator")
        return lexscan.tokenize(expr, (spaceexp, wordexp, numexp, leftPar, rightPar, operator))

    @staticmethod
    def _getRPN(tokens):
        res = []
        stack = []
        for tok in tokens:
            # some utils
            if tok.text in Calculator.constants.keys():
                tok.text = Calculator.constants[tok.text]
                tok.type = 'number'
            elif tok.text == 'x':
                tok.type = 'number'

            if tok.type == 'number':
                res.append(tok)
            elif tok.type == 'function':
                stack.append(tok)
            elif tok.type == 'operator':
                while len(stack) > 0 and (stack[-1].type == 'function' or (stack[-1].type == 'operator' and (Calculator.prec[stack[-1].text] > Calculator.prec[tok.text] or (Calculator.prec[stack[-1].text] == Calculator.prec[tok.text] and Calculator.assoc[stack[-1].text] == 'left')))):
                    res.append(stack.pop())
                stack.append(tok)
            elif tok.type == 'leftPar':
                stack.append(tok)
            elif tok.type == 'rightPar':
                if len(stack) == 0:
                    raise Exception("Mismatched parentheses")
                while stack[-1].type != 'leftPar':
                    res.append(stack.pop())
                    if len(stack) == 0:
                        raise Exception("Mismatched parentheses")
                if stack[-1].type == 'leftPar':
                    stack.pop()
            else:
                raise Exception("Invalid operation")

        while len(stack) > 0:
            top = stack.pop()
            if top.type == 'leftPar' or top.type == 'rightPar':
                raise Exception("Mismatched parentheses")
            res.append(top)

        return res

    @staticmethod
    def _getResult(rpn_tokens, x):
        stack = []
        for tok in rpn_tokens:
            if tok.type == 'function':
                stack.append(float(Calculator.functions[tok.text](stack.pop())))
            elif tok.type == 'operator':
                # TODO: check if empty
                op2 = stack.pop()
                op1 = stack.pop()
                stack.append(float(Calculator.operators[tok.text](op1, op2)))
            else:
                # replace symbolic 'x' with value
                if tok.text == 'x':
                    stack.append(x)
                else:
                    stack.append(float(tok.text))

        return stack.pop()

    def tabulate(self, expr, a, b, n=10):
        """
        :param expr: (str) formulae
        :param a: (float) left end
        :param b: (float) right end
        :return: (np.linspace(a, b, (b-a)//n), values)
        """
        assert b > a, "b must be greater than a"
        assert n > 0, "n must be greater than 0"
        self.expr = expr
        self.tokens = Calculator._getTokens(self.expr)
        self.RPN = Calculator._getRPN(self.tokens)
        x_values = np.linspace(a, b, n)
        y_values = np.array([Calculator._getResult(self.RPN, x) for x in x_values])

        return x_values, y_values

    def plot(self, expr, a, b, n=10):
        x_values, y_values = self.tabulate(expr, a, b, n)
        plt.title(r'$' + expr + '$')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.plot(x_values, y_values)
        plt.show()


if __name__ == "__main__":
    # expression = '2*sin(1/(exp(3*x)+2^3)-tan(x+PI/2))'
    # expression = '2*sin(1/((exp(3*x)+2)^3)-(tan(x+PI/2) + 1))'
    expr = '2*sin(1/(exp(3*x)+2^3)-tan(x+PI/2))'
    a = 0
    b = 1
    n = 20
    try:
        calculator = Calculator()
        x_values, y_values = calculator.tabulate(expr, a, b, n)
        print(x_values)
        print(y_values)
        calculator.plot(expr, a, b, n)
    except Exception as e:
        print(e)
    finally:
        print("Calculation was successful!")
