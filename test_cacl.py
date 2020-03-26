from main import cacl


def test_normal():
    ret = cacl('1')
    assert ret == 1
    ret = cacl('1 + 1')
    assert ret == 2
    ret = cacl('(1)')
    assert ret == 1
    ret = cacl('(1 + 1)')
    assert ret == 2
    ret = cacl('1 * 2')
    assert ret == 2
    ret = cacl('(1 * 2)')
    assert ret == 2
    ret = cacl('(1 + 1) * 2')
    assert ret == 4
    ret = cacl('1 + (1 * 2)')
    assert ret == 3


def test_float():
    ret = cacl('-1.2')
    assert ret == -1.2
    ret = cacl('-.2')
    assert ret == -.2
    ret = cacl('-1.')
    assert ret == -1.
    ret = cacl('-1.2e1')
    assert ret == -12
    ret = cacl('-1.2e-1')
    assert ret == -.12
    ret = cacl('-.2e1')
    assert ret == -2
    ret = cacl('-1.e1')
    assert ret == -10


def test_advanced():
    ret = cacl('-2 + 2')
    assert ret == 0
    ret = cacl('-2^2 + 2')
    assert ret == -2
    ret = cacl('(-2)^2 + 2')
    assert ret == 6
    ret = cacl('+(-2)^2 + 2')
    assert ret == 6
    ret = cacl('(-2)^2^(0 + 2) + 2')
    assert ret == 18
    ret = cacl('((((-2 + 2))))')
    assert ret == 0
    ret = cacl('2^-1')
    assert ret == 0.5
    ret = cacl('- - - + - 1')
    assert ret == 1


def test_func_and_const():
    import math
    ret = cacl('pi')
    assert ret == math.pi
    ret = cacl('sqrt(e)')
    assert ret == math.sqrt(math.e)
    ret = cacl('-sqrt(e)')
    assert ret == -math.sqrt(math.e)
    ret = cacl('-sqrt(e)^2')
    assert ret == -math.sqrt(math.e) ** 2
    ret = cacl('-sqrt(e)^2 * 3')
    assert ret == -math.sqrt(math.e) ** 2 * 3
    ret = cacl('-sqrt(e^3)^2 * 3')
    assert ret == -math.sqrt(math.e ** 3) ** 2 * 3


def test_error():
    def error(code):
        try:
            ret = cacl(code)
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
