from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections
from mininet.cli import CLI
from mininet.clean import cleanup

from subprocess import Popen, PIPE
from time import sleep, time
from multiprocessing import Process
from argparse import ArgumentParser

import sys
import os
import math
import time
import itertools

class OneSwitchTopo(Topo):
    def build(self, n=4):
        hosts = []
        for i in range(1,n+1):
            hosts.append(self.addHost('h%d'%(i)))

        # Here I have created a switch.  If you change its name, its
        # interface names will change from s0-eth1 to newname-eth1.
        switch = self.addSwitch('s0')

        # Add links with appropriate characteristics
        links = []
        for i in range(0, n):
            self.addLink(hosts[i], switch, delay='1s')

class ThreeFastOneSlowTopo(Topo):
    def build(self, n=4):
        hosts = []
        for i in range(1,n+1):
            hosts.append(self.addHost('h%d'%(i)))

        # Here I have created a switch.  If you change its name, its
        # interface names will change from s0-eth1 to newname-eth1.
        switch = self.addSwitch('s0')

        # Add links with appropriate characteristics
        self.addLink(hosts[0], switch, delay='5s')
        for i in range(1, n):
            self.addLink(hosts[i], switch)

def try_dir(path):
    try: 
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise

def start_btc_server(net):
    for host in net.hosts:
        tmp_dir = "./tmp/btc/{}/".format(host.name)
        try_dir(tmp_dir)
        popen = host.popen("bitcoind -regtest -datadir={} -rpcuser=user -rpcpassword=password -rpcport=8332 -daemon".format(tmp_dir))
        print(host.name, popen.communicate())

def stop_btc_server(net):
    host_cli_exec_all(net, "stop")

def btc_server_add_node(net):
    for host, remote in itertools.combinations(net.hosts, 2):
        # popen = host.popen("ping  -c 3 {}".format(remote.IP()))
        # print(popen.communicate())

        addnode_str = 'addnode {} add'.format(remote.IP())
        popen = host.popen(gen_cli_op(host, addnode_str))
        print(host.name, popen.communicate())

def host_cli_exec_all(net, operation):
    for host in net.hosts:
        popen = host.popen(gen_cli_op(host, operation))
        print(host.name, popen.communicate()) 

def gen_cli_op(host, operation):
    tmp_dir = "./tmp/btc/{}/".format(host.name)
    decorated_op = "bitcoin-cli -regtest  -datadir={} -rpcuser=user -rpcpassword=password -rpcport=8332 ".format(tmp_dir) + operation
    print(decorated_op)
    return decorated_op


def simulation():
    # Cleanup any leftovers from previous mininet runs
    cleanup()

    topo = OneSwitchTopo()
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net.start()

    net.pingAll()

    # Start bitcoind for every host
    start_btc_server(net)
    time.sleep(1)

    # Connect all nodes
    btc_server_add_node(net)
    time.sleep(1)

    CLI(net)


    # Stop bitcoind for every host
    stop_btc_server(net)

    net.stop()


simulation()
