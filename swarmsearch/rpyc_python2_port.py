import rpyc
def connect2(ip, port, serviceX):
    print("try2")
    c = rpyc.connect(ip, port, service= serviceX, config={'allow_public_attrs': True}) #create clients in all neighboring services
    return c

def query2(c, querystr):
    result = c.root.search_query(querystr)
    return result