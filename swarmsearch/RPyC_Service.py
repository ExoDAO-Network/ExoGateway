import rpyc
import socket
import sys
import string

sys.path.append('/home/om/Documents/exodao/re-Isearch/swig')
sys.path.append('/home/om/Documents/exodao/re-Isearch/lib')
from IB import *


class SearchService(rpyc.Service):
    ALIASES = ["SearchNode"]
    
    def __init__(self):
        self.IP_set = {"127.0.0.9", "100.100.0.0"} #exposed set of all ip in the network
        self.potential_IP_set=set([])
        
    def on_connect(self, conn):
        # code that runs when a connection is created
        # Add IP of new connection. Sets do not allow duplicates, so the list will only add new IP
        self.IP_set.add(conn.root.showIP())
        pass

    def on_disconnect(self, conn):
        # code that runs after the connection has already closed
        # The service only stores the nodes that are connected
        self.IP_set.remove(conn.root.showIP())
        pass

    def renameService(self,newName):
        self.ALIASES = [newName]
        pass

    def addAlias(self,newAlias):
        self.ALIASES.add(newAlias)
        pass

    def exposed_difference_IPset(self, clientSet): #Return a set that contains the items that only exist on the server and not in client:
        diff_server = self.IP_set.difference(clientSet)
        print(diff_server)
        diff_client = clientSet.copy()
        self.potential_IP_set.add(diff_client.difference(self.IP_set)) #store the IP that need to be checked
        return diff_server

    # def unite_IPset(clientSet) #unite one set with the other, not safe, could have IP which are unwanted
    #     combined = IP_set.union(clientSet)
    #     exposed_IP_set = combined
    #     return combined

    #------- Search Related Stuff ----------
    def exposed_search_query(self,query, args=""):
        
        # this method returns the results of this service
        junk="/tmp/JUNK"
        pdb = IDB(junk)
        squery = SQUERY(query)
        query = QUERY()
        query.SetSQUERY(squery)
        elements = pdb.GetTotalRecords()
        if elements > 0:
            rset = pdb.VSearchSmart(query)
            if not (rset == None):
                total = rset.GetTotalEntries()
            else:
                total = 0
            print( "Searching for: ", query)
            print ("Got = ", total, " Records")
    # Print the results....
            results = []
            for i in range(1, total+1):
                result = rset.GetEntry(i)
                area = pdb.Context(result, "____", "____")
                datum = result.GetDate()
                score = result.GetScore()
                score  = rset.GetScaledScore(score, 100)
                hits   = result.GetHitTable()
                result_dict = {
                    "result": result,
                    "area": area,
                    "datum": datum.RFCdate(),
                    "score": score,
                    "hits": pdb.Present(result, ELEMENT_Brief)
                }
                results.append(result_dict) 
        else:
            print( 'Empty Index!')

        pdb = None
        return results
        #code that searches using the search engine in the defined index
        if (fuzz.ratio(query,sys.argv[2])>50):
            results=(sys.argv[2], "a very long text that nobody will ever read, because it is anyways what they are searching")
        else:
            results=("","no results")        
        return results

    def exposed_centroid_query(self,query, args =""): 
        # this method returns all nodes with relavant centroids
        #INSERT CODE
        #code that searches all centroids in the server file system
        if (True):
            IP_list = self.IP_set
        else:
            IP_list = set([])
        return IP_list
######### CLASS DEFINITION OVER #################

from rpyc.utils.server import ThreadedServer
def StartServer(port=18861):
    t = ThreadedServer(SearchService(), port, protocol_config={'allow_public_attrs': True,})
    t.start()
    return t


print("Server started with hostname= ", sys.argv[1])
t = ThreadedServer(SearchService(),hostname=sys.argv[1], port=18861, protocol_config={'allow_public_attrs': True,})
t.start()
