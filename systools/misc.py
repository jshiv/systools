

def in_ipython(self):
    """Identify environment as IPython or not

    Retuns `bool`
    """
        return '__IPYTHON__' in vars(__builtins__)

def isbooliter(pattern):
    """Identify if patter is list of bools
    Returns `bool`
    """
    return all(map(lambda x: isinstance(x, bool), pattern))

def isboolswitch(pattern):
    """Identify if list is [True, False]
    """
    return isbooliter(patter) and len(pattern)==2 and sum(pattern) == 1
