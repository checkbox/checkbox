def recursive_update(dst, src):
    irecursive_update(dst, src.iteritems())
    return dst

def irecursive_update(a, biter):
    try:
        stack = []
        while biter:
            for (bk,bv) in biter:
                if (bk in a 
                    and isinstance(bv, dict)
                    and isinstance(a[bk], dict)):
                    stack.append((biter, a)) # current -> parent
                    break
                else:
                    a[bk] = bv
            else:
                while not biter:
                    biter, a = stack.pop() # current <- parent 
                continue
            biter, a = bv.iteritems(), a[bk]
    except IndexError:
        pass
