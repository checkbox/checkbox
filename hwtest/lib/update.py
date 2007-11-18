def recursiveupdate(dst, src):
    irecursiveupdate(dst, src.iteritems())
    return dst

def irecursiveupdate(a, biter):
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
