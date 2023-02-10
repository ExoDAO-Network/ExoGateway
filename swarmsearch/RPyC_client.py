import rpyc
import subprocess

def connect2(ip, port, serviceX):
    c = rpyc.connect(ip, port, service= serviceX, config={'allow_public_attrs': True}) #create clients in all neighboring services
    return c

def query2(c, querystr):
    result = c.root.search_query(querystr)
    return result


def query(c, querystr):
    python3_command = "rpyc_python2_port.py " + c + " " + querystr
    print(python3_command)
    process = subprocess.Popen(python3_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print(output)
    print(error)
    return result

def importIP(inputfile): #reads file and returns all ip from list
    # opening the file in read mode
    my_file = open(inputfile, "r")
  
    # reading the file
    data = my_file.read()
      
    # 
    data_into_list = data.split("\n")
    for data in data_into_list:
        data.replace("\n", "")
        if(data == ""):
            data_into_list.remove(data)
      
    # returning the data
    return(set(data_into_list))

class ClientService(rpyc.Service):
    def __init__(self, address):
        self.ip = address
    def exposed_showIP(self):
        return self.ip


