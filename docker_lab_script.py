'''

Author: Manek Gujral 
Created: 28 Sep, 2021

Instructions to implement automated python script

1) docker create auto_ceos1 and auto_ceos2 (2 new containers)

2) docker create auto_net1 and auto_net2 (2 new networks)

3) docker connect x 4 -> both nets with both containers

4) docker start auto_ceos1 and auto_ceos2

5) wait for a few minutes for all EOS agents to start

6) docker network inspect auto_net1 and store in a net1_inspect_list

7) obtain ip address of auto_ceos1 and auto_ceos2

8) docker exec -it ceos1 Cli

9) ping ip_address_auto_ceos2 and vice versa

10) cleanup to ensure script can be run again

'''

'''
Updating Py Script

- add cleanup (-rm) flag, keep alive (-ka) flag, default: rm
- add additional checks before creating or deleting anything
- Modularize code
- add pre conf for container IP
- use docker lib to run commands as opposed to os lib 

'''

#import necessary libraries
import docker 
import os
from time import sleep

print("---------- cEOSLab Python Automation Script ----------")
print()
print("---------- STARTUP ----------")
print()

#use docker lib to create and other docker cmds

# create docker instances with needed environment variables
create_container_1 = "docker create --name=automatic_ceos1 --privileged -e INTFTYPE=eth -e ETBA=1 -e SKIP_ZEROTOUCH_BARRIER_IN_SYSDBINIT=1 -e CEOS=1 -e EOS_PLATFORM=ceoslab -e container=docker -i -t ceosimage:latest /sbin/init systemd.setenv=INTFTYPE=eth systemd.setenv=ETBA=1 systemd.setenv=SKIP_ZEROTOUCH_BARRIER_IN_SYSDBINIT=1 systemd.setenv=CEOS=1 systemd.setenv=EOS_PLATFORM=ceoslab systemd.setenv=container=docker"
create_container_2 = "docker create --name=automatic_ceos2 --privileged -e INTFTYPE=eth -e ETBA=1 -e SKIP_ZEROTOUCH_BARRIER_IN_SYSDBINIT=1 -e CEOS=1 -e EOS_PLATFORM=ceoslab -e container=docker -i -t ceosimage:latest /sbin/init systemd.setenv=INTFTYPE=eth systemd.setenv=ETBA=1 systemd.setenv=SKIP_ZEROTOUCH_BARRIER_IN_SYSDBINIT=1 systemd.setenv=CEOS=1 systemd.setenv=EOS_PLATFORM=ceoslab systemd.setenv=container=docker"
os.system(create_container_1)
os.system(create_container_2)

# start the instances
start_ceos1 = "docker start automatic_ceos1"
start_ceos2 = "docker start automatic_ceos2"
os.system(start_ceos1)
os.system(start_ceos2)

# wait for a few minutes for all EOS agents to start
print()
print("Wait for a few minutes for all EOS agents to start")
print()
sleep(60)

# create docker networks
net1_cmd = "docker network create automatic_net1"
net2_cmd = "docker network create automatic_net2"
os.system(net1_cmd)
os.system(net2_cmd)

# connect docker instances to the networks
connect_cmd1 = "docker network connect automatic_net1 automatic_ceos1"
connect_cmd2 = "docker network connect automatic_net1 automatic_ceos2"
connect_cmd3 = "docker network connect automatic_net2 automatic_ceos1"
connect_cmd4 = "docker network connect automatic_net2 automatic_ceos2"
os.system(connect_cmd1)
os.system(connect_cmd2)
os.system(connect_cmd3)
os.system(connect_cmd4)


#inspect networks
insp_net_1 = "docker network inspect automatic_net1"
insp_net_2 = "docker network inspect automatic_net2"
os.system(insp_net_1)
os.system(insp_net_2)

# init docker lib client
client = docker.DockerClient()

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

print("---------- CLEANUP ---------")
print()

# disconnect docker instances from the networks
connect_cmd1 = "docker network disconnect automatic_net1 automatic_ceos1"
connect_cmd2 = "docker network disconnect automatic_net1 automatic_ceos2"
connect_cmd3 = "docker network disconnect automatic_net2 automatic_ceos1"
connect_cmd4 = "docker network disconnect automatic_net2 automatic_ceos2"
os.system(connect_cmd1)
os.system(connect_cmd2)
os.system(connect_cmd3)
os.system(connect_cmd4)

# delete docker networks
net1_cmd = "docker network rm automatic_net1"
net2_cmd = "docker network rm automatic_net2"
os.system(net1_cmd)
os.system(net2_cmd)

# stop the instances
stop_ceos1 = "docker stop automatic_ceos1"
stop_ceos2 = "docker stop automatic_ceos2"
os.system(stop_ceos1)
os.system(stop_ceos2)

# delete the automated containers to run script again
del_ceos1 = "docker rm automatic_ceos1"
del_ceos2 = "docker rm automatic_ceos2"
os.system(del_ceos1)
os.system(del_ceos2)

print()
print("---------- FINISHED ---------")