import re
import math


class Token():
    operator = 'operator'
    compopr = 'compopr'
    num = 'num'
    newline = 'newline'
    skip = 'skip'
    lparen = 'lparen'
    rparen = 'rparen'
    binopr = 'binopr'
    mismatch = 'mismatch'

    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token(type={self.type}, value={self.value!r}, line={self.line}, column={self.column})"


def tokenize(code):
    """
    词法分析
    """
    token_specification = [
        ('num', r'\d+(\.\d*)?'),  # 整数和小数
        ('newline', r'\n'),  # 回车
        ('skip', r'[ \t]+'),  # 跳过所有空格以及缩进
        ('lparen', r'\('),  # 左圆括号
        ('rparen', r'\)'),  # 右圆括号
        ('compopr', r'(==|!=|>=|<=|>|<)'),  # 比较操作符
        ('binopr', r'(\+|-|\*|/|\^)'),  # 二元操作符
        ('mismatch', r'\S+'),  # 其他未匹配的词
    ]
    tok_regex = r'|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    r = re.compile(tok_regex)
    line_num = 1
    line_start = 0
    for mo in r.finditer(code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start
        if kind == 'num':
            value = float(value) if '.' in value else int(value)
        elif kind == 'newline':
            line_start = mo.end()
            line_num += 1
            continue
        elif kind == 'skip':
            continue
        elif kind == 'mismatch':
            raise RuntimeError(f'{value!r} unexpected on line {line_num}')
        yield Token(kind, value, line_num, column)


class Parser():
    def __init__(self, tokens):
        self.tokens = tokens
        self.lookahead = next(tokens)

    # def output(self, *args, **kwargs):
    #     print(*args, **kwargs, end=' ')

    def exec(self):
        return self.A()

    def match(self, t):
        if t == self.lookahead.value:
            try:
                self.lookahead = next(self.tokens)
            except StopIteration:
                self.tokens = None
            except:
                raise RuntimeError(f'syntex error, {code[:self.lookahead.column] + "^" + code[self.lookahead.column:]}')

    def A(self):
        lvalue = self.B()
        lvalue = self.A_tail(lvalue)
        if self.tokens is not None:
            raise RuntimeError(f'syntex error, {code[:self.lookahead.column] + "^" + code[self.lookahead.column:]}')
        else:
            return lvalue

    def A_tail(self, lvalue):
        if self.lookahead.value == '+':
            self.match('+')
            value = lvalue + self.B()
            return self.A_tail(value)
        elif self.lookahead.value == '-':
            self.match('-')
            value = lvalue - self.B()
            return self.A_tail(value)
        else:
            return lvalue

    def B(self):
        lvalue = self.C()
        return self.B_tail(lvalue)

    def B_tail(self, lvalue):
        if self.lookahead.value == '*':
            self.match('*')
            value = lvalue * self.C()
            return self.B_tail(value)
        elif self.lookahead.value == '/':
            self.match('/')
            value = lvalue / self.C()
            return self.B_tail(value)
        else:
            return lvalue

    def C(self):
        if self.lookahead.value == '+':
            self.match('+')
            value = self.D()
            return value
        elif self.lookahead.value == '-':
            self.match('-')
            value = -self.D()
            return value
        else:
            return self.D()

    def D(self):
        value = self.E()
        if self.lookahead.value == '^':
            self.match('^')
            lvalue = self.C()
            value = value ** lvalue
        return value

    def E(self):
        if self.lookahead.value == '(':
            self.match('(')
            value = self.A()
            self.match(')')
            return value
        elif self.lookahead.type == Token.num:
            value = self.lookahead.value
            self.match(value)
            return value
        else:
            return self.C()


code = '3 + + 3^2'
tokens = tokenize(code)
parser = Parser(tokens)
n = parser.exec()
print(n)
