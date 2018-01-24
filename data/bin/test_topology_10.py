#!/usr/bin/python
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch, UserSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import Link, TCLink


def topology():
  net = Mininet(controller=RemoteController, link=TCLink, switch=OVSKernelSwitch)
  c0 = net.addController( 'c0', controller=RemoteController, ip='192.168.1.239', port=6633 )
  s1 = net.addSwitch('s1')
  s2 = net.addSwitch('s2')
  s3 = net.addSwitch('s3')
  s4 = net.addSwitch('s4')
  s5 = net.addSwitch('s5')
  s6 = net.addSwitch('s6')
  s7 = net.addSwitch('s7')
  s8 = net.addSwitch('s8')
  s9 = net.addSwitch('s9')
  s10 = net.addSwitch('s10')
  h1 = net.addHost('h1')
  net.addLink(s1, h1)
  h2 = net.addHost('h2')
  net.addLink(s2, h2)
  h3 = net.addHost('h3')
  net.addLink(s7, h3)
  h4 = net.addHost('h4')
  net.addLink(s10, h4)
  h5 = net.addHost('h5')
  net.addLink(s2, h5)
  h6 = net.addHost('h6')
  net.addLink(s9, h6)
  h7 = net.addHost('h7')
  net.addLink(s5, h7)
  h8 = net.addHost('h8')
  net.addLink(s4, h8)
  h9 = net.addHost('h9')
  net.addLink(s7, h9)
  h10 = net.addHost('h10')
  net.addLink(s7, h10)
  net.addLink(s1, s4)
  net.addLink(s1, s8)
  net.addLink(s2, s8)
  net.addLink(s2, s10)
  net.addLink(s3, s6)
  net.addLink(s4, s9)
  net.addLink(s5, s10)
  net.addLink(s6, s9)
  net.addLink(s7, s9)
  net.build()
  c0.start()
  s1.start([c0])
  s2.start([c0])
  s3.start([c0])
  s4.start([c0])
  s5.start([c0])
  s6.start([c0])
  s7.start([c0])
  s8.start([c0])
  s9.start([c0])
  s10.start([c0])
  CLI( net )
  net.stop()


if __name__ == '__main__':
  setLogLevel( 'info' )
  topology()
