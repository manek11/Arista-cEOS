'''

Author: Manek Gujral 
Created: 29 Sep, 2021

Updating Py Script

- add cleanup (-rm) flag
- add additional checks before creating or deleting anything
- Modularize code
- use docker lib to run commands as opposed to os lib 

'''

# import necessary libraries
import docker 
import os
from time import sleep
import sys

#Functions that script will use

# function to check if container exists
def container_running_check(name):
    client = docker.DockerClient()
    container_list = client.containers.list()

    for i in range(len(container_list)):
        curr_container = container_list[i]
        curr_container_name = curr_container.attrs['Name']
        if(curr_container_name == "/"+name):
            return True

    return False        

def network_running_check(network_name):
    client = docker.DockerClient()
    network_list = client.networks.list()

    for i in range(len(network_list)):
        curr_network = network_list[i]
        curr_network_name = curr_network.name
        if(curr_network_name == network_name):
            return True

    return False  

def create_containers():
    #create the docker containers and start them
    client = docker.DockerClient()

    ENVIRONMENT = {'CEOS': '1',
                'container': 'docker',
                'EOS_PLATFORM': 'ceoslab',
                'SKIP_ZEROTOUCH_BARRIER_IN_SYSDBINIT': '1',
                'ETBA': '1',
                'INTFTYPE': 'eth'
                }

    auto_ceos1 = client.containers.create(image='ceosimage', command='/sbin/init systemd.setenv=INTFTYPE=eth systemd.setenv=ETBA=1 systemd.setenv=SKIP_ZEROTOUCH_BARRIER_IN_SYSDBINIT=1 systemd.setenv=CEOS=1 systemd.setenv=EOS_PLATFORM=ceoslab systemd.setenv=container=docker', name='automatic_ceos1', hostname='ceos',
                                               environment=ENVIRONMENT, stdin_open=True, tty=True,
                                               privileged=True)               

    auto_ceos2 = client.containers.create(image='ceosimage', command='/sbin/init systemd.setenv=INTFTYPE=eth systemd.setenv=ETBA=1 systemd.setenv=SKIP_ZEROTOUCH_BARRIER_IN_SYSDBINIT=1 systemd.setenv=CEOS=1 systemd.setenv=EOS_PLATFORM=ceoslab systemd.setenv=container=docker', name='automatic_ceos2', hostname='ceos',
                                               environment=ENVIRONMENT, stdin_open=True, tty=True,
                                               privileged=True)               

    auto_ceos1.start()
    auto_ceos2.start()

    # wait for a few minutes for all EOS agents to start
    print()
    print("Wait for a few minutes for all EOS agents to start")
    print()
    sleep(60)

    return auto_ceos1, auto_ceos2


def create_networks():
    client = docker.DockerClient()

    # create docker networks
    net1_cmd = client.networks.create("automatic_net1", driver="bridge")
    net2_cmd = client.networks.create("automatic_net2", driver="bridge")

    # connect docker instances to the networks
    net1_cmd.connect("automatic_ceos1")
    net1_cmd.connect("automatic_ceos2")
    net2_cmd.connect("automatic_ceos1")
    net2_cmd.connect("automatic_ceos2")

    return net1_cmd, net2_cmd


def inspect_networks():
    #inspect networks
    insp_net_1 = "docker network inspect automatic_net1"
    insp_net_2 = "docker network inspect automatic_net2"
    os.system(insp_net_1)
    os.system(insp_net_2)


def cleanup(net1_cmd, net2_cmd, auto_ceos1, auto_ceos2):
    if(container_running_check("automatic_ceos1") == True and container_running_check("automatic_ceos2") == True
        and network_running_check("automatic_net1") == True and network_running_check("automatic_net2") == True):
        
        print("---------- CLEANUP ---------")
        print()

        # disconnect docker instances from the networks
        net1_cmd.disconnect("automatic_ceos1")
        net1_cmd.disconnect("automatic_ceos2")
        net2_cmd.disconnect("automatic_ceos1")
        net2_cmd.disconnect("automatic_ceos2")

        # delete docker networks
        net1_cmd.remove()
        net2_cmd.remove()

        #stop networks
        auto_ceos1.stop()
        auto_ceos2.stop()        

        #delete networks
        auto_ceos1.remove()
        auto_ceos2.remove()  

#------------------------------------------------------------------------------------------------------------------------------------------#

auto_ceos1 = None
auto_ceos2 = None
net1_cmd = None
net2_cmd = None

# checking for -rm flag for cleanup
if(len(sys.argv) > 1):
    flag = sys.argv[1]
else:
    flag = '-none'

print("---------- cEOSLab Python Automation Script ----------")
print()
print("---------- STARTUP ----------")
print()

# init docker lib client
client = docker.DockerClient()

if(container_running_check("automatic_ceos1") == False and container_running_check("automatic_ceos2") == False):
    auto_ceos1, auto_ceos2 = create_containers()


if( network_running_check("automatic_net1") == False and network_running_check("automatic_net2") == False):
    net1_cmd, net2_cmd = create_networks()


inspect_networks()

# obtain IP Address of both containers via indexing through container atttributes
container_1 = client.containers.get("automatic_ceos1")
container_1_ip_addr = container_1.attrs['NetworkSettings']['IPAddress']
print()
print("IP Address of auto_ceos1 = " + container_1_ip_addr)
print()

container_2 = client.containers.get("automatic_ceos2")
container_2_ip_addr = container_2.attrs['NetworkSettings']['IPAddress']
print("IP Address of auto_ceos2 = " + container_2_ip_addr)
print()

#initiate ping test both ways
print("Ping Test from auto_ceos1 to auto_ceos2")
print()
ping_str = "ping " + container_2_ip_addr
ping_str = '"%s"' % ping_str
ping_cmd = 'docker exec -it automatic_ceos1 Cli -c ' + ping_str
os.system(ping_cmd)

print("Ping Test from auto_ceos2 to auto_ceos1")
print()
ping_str = "ping " + container_1_ip_addr
ping_str = '"%s"' % ping_str
ping_cmd = 'docker exec -it automatic_ceos2 Cli -c ' + ping_str
os.system(ping_cmd)

print()
print("---------- AUTOMATION COMPLETE ----------")
print()

if (flag == '-rm'):
    client = docker.DockerClient()

    network_list = client.networks.list()

    auto_ceos1 = client.containers.get("automatic_ceos1")
    auto_ceos2 = client.containers.get("automatic_ceos2")

    for i in range(len(network_list)):
        curr_network = network_list[i]
        curr_network_name = curr_network.name

        if(curr_network_name == "automatic_net1"):
            net1_cmd = client.networks.get(curr_network.id)

        if(curr_network_name == "automatic_net2"):
            net2_cmd = client.networks.get(curr_network.id)

    cleanup(net1_cmd, net2_cmd, auto_ceos1, auto_ceos2)

print()
print("---------- FINISHED ---------")

 

