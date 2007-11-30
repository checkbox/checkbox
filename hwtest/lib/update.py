def recursive_update(dst, src):
    irecursive_update(dst, list(src.iteritems()))
    return dst

def irecursive_update(a, blist):
    try:
        stack = []
        while blist:
            while blist:
                (bk, bv) = blist.pop(0)
                if (bk in a 
                     and isinstance(bv, dict)
                     and isinstance(a[bk], dict)):
                    stack.append((blist, a)) # current -> parent
                    break
                else:
                    a[bk] = bv
            else:
                while not blist:
                    blist, a = stack.pop() # current <- parent 
                continue
            blist, a = list(bv.iteritems()), a[bk]
    except IndexError:
        pass
