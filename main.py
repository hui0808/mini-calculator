import re
import math
from enum import Enum


class TokenEnum(Enum):
    num = 1
    newline = 2
    skip = 3
    lparen = 4
    rparen = 5
    compopr = 6
    binopr = 7
    const = 8
    mismatch = 9


class Token():

    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token(type={self.type}, value={self.value!r}, line={self.line}, column={self.column})"

    @staticmethod
    def tokenize(code):
        """
        词法分析
        """
        token_specification = [
            (TokenEnum.num, r'\d+(\.\d*)?'),  # 整数和小数
            (TokenEnum.newline, r'\n'),  # 回车
            (TokenEnum.skip, r'[ \t]+'),  # 跳过所有空格以及缩进
            (TokenEnum.lparen, r'\('),  # 左圆括号
            (TokenEnum.rparen, r'\)'),  # 右圆括号
            (TokenEnum.compopr, r'(==|!=|>=|<=|>|<)'),  # 比较操作符
            (TokenEnum.binopr, r'(\+|-|\*|/|\^)'),  # 二元操作符
            (TokenEnum.const, r'(exp|pi|tau)'),  # 常量
            (TokenEnum.mismatch, r'\S+'),  # 其他未匹配的词
        ]
        tok_regex = r'|'.join(f'(?P<{pair[0].name}>{pair[1]})' for pair in token_specification)
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
            elif kind == 'skip':
                continue
            elif kind == 'mismatch':
                raise Exception(f'{value!r} unexpected on line {line_num}')
            yield Token(TokenEnum[kind], value, line_num, column)


class Parser():
    def __init__(self):
        self.code = None
        self.tokens = None
        self.lookahead = None

    def error(self):
        raise Exception(f'syntex error, {self.code[:self.lookahead.column] + "?" + self.code[self.lookahead.column:]}')

    def exec(self, code):
        self.code = code
        self.tokens = Token.tokenize(code)
        try:
            self.lookahead = next(self.tokens)
        except StopIteration:
            return None
        value = self.A()
        if self.tokens is not None:
            self.error()
        return value

    def match(self, t):
        if self.tokens is None:
            self.error()
        elif t == self.lookahead.value:
            try:
                self.lookahead = next(self.tokens)
            except StopIteration:
                self.tokens = None

    def A(self):
        lvalue = self.B()
        return self.A_tail(lvalue)

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
        elif self.lookahead.type == TokenEnum.num:
            value = self.lookahead.value
            self.match(value)
            return value
        else:
            return self.C()


if __name__ == '__main__':
    parser = Parser()
    while True:
        i = input('>> ')
        n = parser.exec(i)
        if n is None:
            continue
        print('>>', n)
