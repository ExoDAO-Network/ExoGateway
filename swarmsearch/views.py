from django.shortcuts import render
from.models import SwarmNode, Tag
from . import RPyC_client as RC
import xmlrpc.client
import socket
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

#TODO: move to library file for clarity
### business logic ###        



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
                if(any(node==mynode.data for mynode in elist)):
                    elist.remove(myNode)
                for newIp in details["storedIP"]:
                    newNode = SwarmNode.objects.filter(ip=newIp)
                    if not newNode:
                        newNode = SwarmNode.objects.create(ip=newIp)
                        nodes.append(newNode)
            else:
                myNode=localNode(node, c, False)
                if(not any(node==mynode.data for mynode in elist)):
                    elist.append(myNode)

    tags = Tag.objects.all()
    context = {'nodes': cList, 'offline':elist, 'tags':tags}


    return render(request, 'home.html', context)

def results(request):

    query_results = [{"logic": "RSS",
                        "feed_title": "duckduck",
                        "title": "blabla",
                        "link": "http://www.duckduckgo.com",
                        "published": "1st of February 1999",
                        "match": "Hit was here __query__"},
                        {"logic": "RSS",
                        "feed_title": "NYTimes",
                        "title": "blabla2",
                        "link": "http://www.nyt.com",
                        "published": "1st of February 1999",
                        "match": "Hit was here __query__"},
                        {"logic": "RSS",
                        "feed_title": "wiki",
                        "title": "blabla3",
                        "link": "http://www.wikipedia.com",
                        "published": "1st of February 1999",
                        "match": "Hit was here __query__"},
                        ]
    if request.method == 'POST':
        querystr = str(request.POST.get('query', None))
        tags = request.POST.getlist('Tag_value', None)
        print(tags)
        for Cl in  cList:
            test = 0
            if(('all' in tags) or (str(Cl.data.tag) in tags) or (str(Cl.data.ownerTag) in tags)):
                try:
                    test = Cl.rpc.execute_query(querystr) #Cl.root.search_query(querystr)
                    for res in test:
                        query_results.append(res)
                except:
                    print("error")
            
    context = {'queryresults': query_results}
    return render(request, 'results.html', context)
# Create your views here.
