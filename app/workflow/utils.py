
def fill_args(structure,args):
    for n in structure:
        for k,v in n.items():
            if type(v) == str and v[0] == "$" and v[1:] in args:
                n[k] = args[v[1:]]        
