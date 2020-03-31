import re
import math
from enum import Enum
import os

os.system("")


class TokenEnum(Enum):
    num = 1
    newline = 2
    skip = 3
    lparen = 4
    rparen = 5
    compopr = 6
    binopr = 7
    const = 8
    func = 9
    end = 10
    mismatch = 11


class Token():
    def __init__(self, type, value, line, start, end, line_text):
        self.type = type
        self.value = value
        self.line = line
        self.start = start
        self.end = end
        self.line_text = line_text

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, {(self.line, (self.start, self.end))}, {self.line_text!r})"

    @staticmethod
    def tokenize(code):
        """
        词法分析
        """
        token_specification = [
            (TokenEnum.num, r'(\d+(\.\d*)?|\.\d+)([Ee][\+-]?\d+)?'),  # 整数、小数、科学计数法
            (TokenEnum.newline, r'\n'),  # 回车
            (TokenEnum.skip, r'[ \t]+'),  # 跳过所有空格以及缩进
            (TokenEnum.lparen, r'\('),  # 左圆括号
            (TokenEnum.rparen, r'\)'),  # 右圆括号
            (TokenEnum.compopr, r'(==|!=|>=|<=|>|<)'),  # 比较操作符
            (TokenEnum.binopr, r'(\+|-|\*|/|\^|%)'),  # 二元操作符
            (TokenEnum.const, r'(e|pi|tau)'),  # 常量
            (TokenEnum.func, r'(log10|log2|log|sqrt|cos|sin|tan|acos|asin|atan)'),  # 函数
            (TokenEnum.end, r'$'),  # 结束
            (TokenEnum.mismatch, r'\S+'),  # 其他未匹配的词
        ]
        tok_regex = r'|'.join(f'(?P<{pair[0].name}>{pair[1]})' for pair in token_specification)
        r = re.compile(tok_regex)
        line_num = 1
        line_start = 0
        line_list = code.split('\n')
        line_list.append('')
        for mo in r.finditer(code):
            kind = mo.lastgroup
            value = mo.group()
            start = mo.start() - line_start
            end = mo.end() - line_start
            cur_line = line_list[line_num - 1]
            if kind == 'num':
                if '.' in value or 'e' in value or 'E' in value:
                    value = float(value)
                else:
                    value = int(value)
            elif kind == 'const':
                value = vars(math)[value]
            elif kind == 'func':
                value = vars(math)[value]
            elif kind == 'newline':
                line_start = mo.end()
                line_num += 1
            elif kind == 'skip':
                continue
            elif kind == 'mismatch':
                f = cur_line[:start] + f'\033[4;1;31m{cur_line[start:end]}\033[0m' + cur_line[end:]
                raise Exception(f'Line {line_num}: {f} unexpected')
            yield Token(TokenEnum[kind], value, line_num, start, end, cur_line)


class Parser():
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.lookahead = next(tokenizer)

    def error(self):
        line = self.lookahead.line_text
        line_num = self.lookahead.line
        start = self.lookahead.start
        end = self.lookahead.end
        if self.lookahead.type == TokenEnum.end:
            start -= 1
        f = line[:start] + f'\033[4;1;31m{line[start:end]}\033[0m' + line[end:]
        raise Exception(f'Line {line_num}: {f} syntex error')

    def exec(self):
        if self.lookahead.type == TokenEnum.end:
            return None
        value = self.A()
        self.match(TokenEnum.end)
        return value

    def match(self, t):
        if self.lookahead.value == t or self.lookahead.type == t:
            try:
                self.lookahead = next(self.tokenizer)
            except StopIteration:
                self.tokenizer = None
        else:
            self.error()

    def A(self):
        """
        A -> B A_tail
        """
        lvalue = self.B()
        return self.A_tail(lvalue)

    def A_tail(self, lvalue):
        """
        A_tail -> + B A_tail | - B A_tail | ε
        """
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
        """
        B -> C B_tail
        """
        lvalue = self.C()
        return self.B_tail(lvalue)

    def B_tail(self, lvalue):
        """
        B_tail -> * C B_tail | / C B_tail | % C B_tail | ε
        """
        if self.lookahead.value == '*':
            self.match('*')
            value = lvalue * self.C()
            return self.B_tail(value)
        elif self.lookahead.value == '/':
            self.match('/')
            value = lvalue / self.C()
            return self.B_tail(value)
        elif self.lookahead.value == '%':
            self.match('%')
            value = lvalue % self.C()
            return self.B_tail(value)
        else:
            return lvalue

    def C(self):
        """
        C -> + D | - D | D
        """
        if self.lookahead.value == '+':
            self.match('+')
            return self.D()
        elif self.lookahead.value == '-':
            self.match('-')
            return -self.D()
        else:
            return self.D()

    def D(self):
        """
        D -> E ^ C | E
        """
        value = self.E()
        if self.lookahead.value == '^':
            self.match('^')
            lvalue = self.C()
            value = value ** lvalue
        return value

    def E(self):
        """
        E -> num | const | ( A ) | func ( A ) | + C | - C
        """
        if self.lookahead.value == '(':
            self.match('(')
            value = self.A()
            self.match(')')
            return value
        elif self.lookahead.type == TokenEnum.func:
            func = self.lookahead.value
            self.match(func)
            self.match('(')
            value = self.A()
            self.match(')')
            return func(value)
        elif self.lookahead.type == TokenEnum.num:
            value = self.lookahead.value
            self.match(value)
            return value
        elif self.lookahead.type == TokenEnum.const:
            value = self.lookahead.value
            self.match(self.lookahead.value)
            return value
        elif self.lookahead.value == '+':
            self.match('+')
            return self.C()
        elif self.lookahead.value == '-':
            self.match('-')
            return -self.C()
        else:
            self.error()


def calc(code):
    tokengen = Token.tokenize(code)
    p = Parser(tokengen)
    n = p.exec()
    return n


if __name__ == '__main__':
    while True:
        try:
            i = input('>> ')
            n = calc(i)
            if n is None:
                continue
            print('>>', n)
        except Exception as e:
            print('>>', e)
