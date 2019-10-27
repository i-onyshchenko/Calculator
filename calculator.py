# Created by Ihor Onyshchenko, 2019. All rights reserved.

import lexscan
from math import pi, sin, cos, tan, log, sqrt, exp
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint


class Calculator:
    prec = {'^': 4, '*': 3, '/': 3, '%': 3, '+': 2, '-': 2}
    assoc = {'^': 'right', '*': 'left', '/': 'left', '%': 'left', '+': 'left', '-': 'left'}
    constants = {'PI': pi}
    operators = {'+': lambda x, y: x+y, '-': lambda x, y: x - y, '*': lambda x, y: x*y, '/': lambda x, y: x/y, '%': lambda x, y: x % y, '^': lambda x, y: x**y}
    functions = {'sin': lambda x: sin(x), 'cos': lambda x: cos(x),
                 'tan': lambda x: tan(x), 'log': lambda x: log(x),
                 'sqrt': lambda x: sqrt(x), 'exp': lambda x: exp(x),
                 'unary_minus': lambda x: -x}

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
        numexp = lexscan.ScanExp(r'[0-9]*\.?[0-9]+', name="number")
        leftPar = lexscan.ScanExp(r'\(', name="leftPar")
        rightPar = lexscan.ScanExp(r'\)', name="rightPar")
        operator = lexscan.ScanExp(r'[\+\-\*\/\^\%]', name="operator")
        badentry = lexscan.ScanExp(r'[\$\,\\\@\#\!\&\~\=]', name="badentry")
        return lexscan.tokenize(expr, (spaceexp, wordexp, numexp, leftPar, rightPar, operator, badentry))

    @staticmethod
    def _getRPN(tokens):
        res = []
        stack = []
        for (i, tok) in enumerate(tokens):
            # some utils
            if tok.type == 'badentry':
                raise Exception('невідомий символ.')
            if tok.text in Calculator.constants.keys():
                tok.text = Calculator.constants[tok.text]
                tok.type = 'number'
            elif tok.text == 'x':
                tok.type = 'number'

            if tok.text == '-' and (i == 0 or tokens[i-1].type == 'operator' or tokens[i-1].type == 'leftPar'):
                tok.type = 'function'
                tok.text = 'unary_minus'

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
                    raise Exception("перевірте дужки.")
                while stack[-1].type != 'leftPar':
                    res.append(stack.pop())
                    if len(stack) == 0:
                        raise Exception("перевірте дужки.")
                if stack[-1].type == 'leftPar':
                    stack.pop()
            else:
                raise Exception("неіснуюча операція.")

        while len(stack) > 0:
            top = stack.pop()
            if top.type == 'leftPar' or top.type == 'rightPar':
                raise Exception("перевірте дужки.")
            res.append(top)

        return res

    @staticmethod
    def _getResult(rpn_tokens, x):
        stack = []
        for tok in rpn_tokens:
            if tok.type == 'function':
                try:
                    stack.append(float(Calculator.functions[tok.text](stack.pop())))
                except ValueError:
                    raise Exception('некоректний аргумент функції.')
                except:
                    raise Exception("неімплементована функція.")
            elif tok.type == 'operator':
                if len(stack) == 0:
                    raise Exception("недостатня кількість операндів.")
                op2 = stack.pop()
                if len(stack) == 0:
                    raise Exception("недостатня кількість операндів.")
                op1 = stack.pop()
                try:
                    stack.append(float(Calculator.operators[tok.text](op1, op2)))
                except ZeroDivisionError:
                    raise Exception('ділення на нуль')
                except:
                    raise Exception("неімплементований оператор.")
            else:
                # replace symbolic 'x' with value
                if tok.text == 'x':
                    stack.append(x)
                else:
                    stack.append(float(tok.text))

        res = stack.pop()
        if len(stack) > 0:
            print(stack)
            raise Exception('вираз містить забагато аргументів.')
        return res

    def tabulate(self, expr, a, b, n=10):
        """
        :param expr: (str) formulae
        :param a: (float) left end
        :param b: (float) right end
        :param n: (int) number of points
        :return: (np.linspace(a, b, (b-a)//n), values)
        """
        try:
            a = float(a)
            b = float(b)
            n = int(n)
        except ValueError:
            raise Exception('некоректні параметри табуляції.')
        assert b >= a, "b має бути не меншим за a."
        assert n > 0, "n має бути додатнім."
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
    expr = '2*sin(1/((exp(3*x)+2)^3)-(tan(x+PI/2) + 1))'
    # expr = '2*sin(1/(exp(3*x)+2^3)-tan(x+PI/2))'
    # expr = '2*sen(25)'
    a = 0
    b = 10
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
        print("Done!")
