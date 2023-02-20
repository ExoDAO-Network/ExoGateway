from django.shortcuts import render
from.models import SwarmNode, Tag
import xmlrpc.client
import socket
import base64
from .forms import SwarmNodeForm
import importlib
from datetime import datetime
class localNode():
    def __init__(self, node, rpcService=None, connect=False):
        self.data = node
        self.connected = connect
        self.selected = True
        self.rpc=rpcService
    
cList=[] #list of connected nodes
sList =[] #list of nodes we want to search
elist=[] #list of nodes that did not connect
alltags=[] #list of all existing tags

#TODO: move to library file for clarity
### business logic ###        

def decode_base64(input):
    base64_string =input
    base64_bytes = base64_string.encode("ISO-8859-1")
    
    sample_string_bytes = base64.b64decode(base64_bytes + b'==')
    output_string = sample_string_bytes.decode("ISO-8859-1", 'ignore')
    return output_string

def _get_rpc(ip, port): 
    a = xmlrpc.client.ServerProxy('http://'+str(ip)+':'+ str(port))

    try:
        success= a.con_test()   # Call a status test method.
        if(success): 
            print("connected:", ip)
    except xmlrpc.client.Fault:
        # connected to the server and the method doesn't exist. 
        print("faulty method:" , ip)
        pass
    except socket.error:
        # Not connected ; socket error mean that the service is unreachable.
        print("no connection:" , ip)
        return False, None
    except:
        #something else
        print("connect error:" , ip)
        return False, None
    return True, a

def check_node_connections(nodes, IPset, port=18861):
    socket.setdefaulttimeout(0.5)        #set the timeout to 0.5 seconds 
    for node in nodes:
        IPset.add(str(node.ip))  #extract ipset from db for sharing with nodes
    for Cl in cList:               #check if node is still connected
        try:
            if(not Cl.rpc.con_test()):
                elist.append(Cl)
                cList.remove(Cl)
        
        except Exception as e:
            print("Error in Service: ", Cl.data.name, str(e))
            elist.append(Cl)
            cList.remove(Cl)
    for node in nodes:
        if(not any(node==mynode.data for mynode in cList)): #go through new connection procedure for every not connected node
            success,c=_get_rpc(node.ip, port) #try to buld connection
            if(success):
                iplist=list(IPset)
                details=c.get_Node_details(iplist)

                node.name=str(details["name"])
                node.ownerTag=str(details["tags"])
                Tag.objects.update_or_create(name=node.ownerTag)
                node.description=str(details["description"])

                date_format = "%Y%m%dT%X"
                a = datetime.strptime(str(details["onlineTime"]), date_format)
                node.onTime=a
                node.save() #save details to database
                myNode=localNode(node, c, True) #create new instance for list
                cList.append(myNode) #add to connected nodes list
                try:
                    #we only checked cList before, 
                    #in case we created a connection with a node in elist, remove from there:
                    elist.remove(any(node==mynode.data for mynode in elist))
                except:
                    print("nothing to remove")
                for newIp in details["storedIP"]: #we also got IP from the node we connected to, add them to our Gateway DB
                    newNode = SwarmNode.objects.filter(ip=newIp)
                    if not newNode:
                        newNode = SwarmNode.objects.create(ip=newIp)
                        nodes.append(newNode)
            else:
                myNode=localNode(node, c, False)
                if(not any(node==mynode.data for mynode in elist)):
                    elist.append(myNode)
    socket.setdefaulttimeout(5)        #set the timeout to 5 seconds 

##### website rendering ####
def home(request):
    nodes = SwarmNode.objects.all()
    nodes= list(nodes)
    IPset = set([])

    check_node_connections(nodes, IPset)
    

    alltags = Tag.objects.all()

    context = {'nodes': cList, 'offline':elist, 'tags':alltags}


    return render(request, 'home.html', context)

def results(request):
    alltags = Tag.objects.all()

    nodes = SwarmNode.objects.all()
    nodes= list(nodes)
    IPset = set([])

    check_node_connections(nodes, IPset)
    query_results = []
    if request.method == 'POST':
        querystr = str(request.POST.get('query', None))
        tags = request.POST.getlist('Tag_value', None)
        query_arg1=str(request.POST.get('normalization', None))
        query_arg2=str(request.POST.get('sorting', None))
        if(len(tags) == 0):
            tags.append('all')
        for Cl in  cList:
            test = 0
            if(('all' in tags) or (str(Cl.data.ownerTag) in tags)):
                try:
                    test = Cl.rpc.execute_query(querystr,query_arg1, query_arg2) #Cl.root.search_query(querystr)
                    for res in test:
                        for key in res:
                            res[key]=decode_base64(res[key])
                        res['node']=Cl
                        query_results.append(res)
                except Exception as e:
                    print("Error in Service: ", Cl.data.name, str(e))
        print(tags)
    context = {'queryresults': query_results, 'query': querystr, 'nodes': cList, 'offline':elist, 'selected_tags':tags,  'tags':alltags,'selected_normalization':query_arg1, "selected_sorting": query_arg2}
    return render(request, 'results.html', context)
# Create your views here.
