from django.shortcuts import render
from.models import SwarmNode, Tag
from . import RPyC_client as RC
import xmlrpc.client
import socket
import base64
from .forms import SwarmNodeForm
from datetime import datetime
class localNode():
    def __init__(self, node, rpcService=None, connect=False):
        self.data = node
        self.connected = connect
        self.selected = True
        self.rpc=rpcService
    
cList=[]
sList =[]
elist=[]
alltags=[]
#TODO: move to library file for clarity
### business logic ###        

def decode_base64(input):
    base64_string =input
    base64_bytes = base64_string.encode("ascii")
    
    sample_string_bytes = base64.b64decode(base64_bytes + b'==')
    output_string = sample_string_bytes.decode("ascii")
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


##### website rendering ####
def home(request):
    port=18861
    nodes = SwarmNode.objects.all()
    nodes= list(nodes)
    IPset = set([])

    socket.setdefaulttimeout(0.5)        #set the timeout to 0.5 seconds 
    for node in nodes:
        IPset.add(str(node.ip))
    for node in nodes:
        if(not any(node==mynode.data for mynode in cList)):
            success,c=_get_rpc(node.ip, port)
            if(success):
                iplist=list(IPset)
                details=c.get_Node_details(iplist)
                print(details)

                node.name=str(details["name"])
                node.ownerTag=str(details["tags"])
                Tag.objects.update_or_create(name=node.ownerTag)
                node.description=str(details["description"])

                date_format = "%Y%m%dT%X"
                a = datetime.strptime(str(details["onlineTime"]), date_format)
                node.onTime=a
                node.save()
                myNode=localNode(node, c, True)
                cList.append(myNode)
                try:
                    elist.remove(any(node==mynode.data for mynode in elist))
                except:
                    print("nothing to remove")
                for newIp in details["storedIP"]:
                    newNode = SwarmNode.objects.filter(ip=newIp)
                    if not newNode:
                        newNode = SwarmNode.objects.create(ip=newIp)
                        nodes.append(newNode)
            else:
                myNode=localNode(node, c, False)
                if(not any(node==mynode.data for mynode in elist)):
                    elist.append(myNode)

    alltags = Tag.objects.all()

    socket.setdefaulttimeout(5)        #set the timeout to 0.5 seconds 
    context = {'nodes': cList, 'offline':elist, 'tags':alltags}


    return render(request, 'home.html', context)

def results(request):
    alltags = Tag.objects.all()
    query_results = []
    if request.method == 'POST':
        querystr = str(request.POST.get('query', None))
        tags = request.POST.getlist('Tag_value', None)
        for Cl in  cList:
            test = 0
            if(('all' in tags) or (str(Cl.data.tag) in tags) or (str(Cl.data.ownerTag) in tags)):
                
                test = Cl.rpc.execute_query(querystr) #Cl.root.search_query(querystr)
                for res in test:
                    print(res)
                    for key in res:
                        res[key]=decode_base64(res[key])
                    query_results.append(res)
                    print(res)
            
    context = {'queryresults': query_results,'nodes': cList, 'offline':elist, 'tags':alltags}
    return render(request, 'results.html', context)
# Create your views here.
