
def fill_args(structure,workflow_args,args):
    for n in structure:
        for k,v in n.items():
            print(k,v)
            if type(v) == str and v[0] == "$" and v[1:] in args:
                n[k] = args[v[1:]]
            elif  type(v) == str and v[0] == "$" and v[1:] in workflow_args:
                if "default" in workflow_args[v[1:]]:
                    n[k] = workflow_args[v[1:]]["default"]
            print(k,n[k])
