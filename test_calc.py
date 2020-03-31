from main import calc


def test_normal():
    ret = calc('1')
    assert ret == 1
    ret = calc('1 + 1')
    assert ret == 2
    ret = calc('(1)')
    assert ret == 1
    ret = calc('(1 + 1)')
    assert ret == 2
    ret = calc('1 * 2')
    assert ret == 2
    ret = calc('(1 * 2)')
    assert ret == 2
    ret = calc('(1 + 1) * 2')
    assert ret == 4
    ret = calc('1 + (1 * 2)')
    assert ret == 3
    ret = calc('-1 * -2')
    assert ret == 2


def test_float():
    ret = calc('-1.2')
    assert ret == -1.2
    ret = calc('-.2')
    assert ret == -.2
    ret = calc('-1.')
    assert ret == -1.
    ret = calc('-1.2e1')
    assert ret == -12
    ret = calc('-1.2e-1')
    assert ret == -.12
    ret = calc('-.2e1')
    assert ret == -2
    ret = calc('-1.e1')
    assert ret == -10


def test_advanced():
    ret = calc('-2 + 2')
    assert ret == 0
    ret = calc('-2^2 + 2')
    assert ret == -2
    ret = calc('(-2)^2 + 2')
    assert ret == 6
    ret = calc('+(-2)^2 + 2')
    assert ret == 6
    ret = calc('(-2)^2^(0 + 2) + 2')
    assert ret == 18
    ret = calc('((((-2 + 2))))')
    assert ret == 0
    ret = calc('2^-1')
    assert ret == 0.5
    ret = calc('- - - + - 1')
    assert ret == 1


def test_func_and_const():
    import math
    ret = calc('pi')
    assert ret == math.pi
    ret = calc('sqrt(e)')
    assert ret == math.sqrt(math.e)
    ret = calc('-sqrt(e)')
    assert ret == -math.sqrt(math.e)
    ret = calc('-sqrt(e)^2')
    assert ret == -math.sqrt(math.e) ** 2
    ret = calc('-sqrt(e)^2 * 3')
    assert ret == -math.sqrt(math.e) ** 2 * 3
    ret = calc('-sqrt(e^3)^2 * 3')
    assert ret == -math.sqrt(math.e ** 3) ** 2 * 3


def test_error():
    def error(code):
        try:
            ret = calc(code)
        except Exception:
            ret = None
        assert ret == None

    error('pip')
    error('sqrt(2')
    error('')
    error('()')
    error('(())')
    error('(()')
    error('+')
    error(')')
    error('2+')
    error('2^')
    error('2e')
    error('2e1.1')
