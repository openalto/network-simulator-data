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
  s11 = net.addSwitch('s11')
  s12 = net.addSwitch('s12')
  s13 = net.addSwitch('s13')
  s14 = net.addSwitch('s14')
  s15 = net.addSwitch('s15')
  s16 = net.addSwitch('s16')
  s17 = net.addSwitch('s17')
  s18 = net.addSwitch('s18')
  s19 = net.addSwitch('s19')
  s20 = net.addSwitch('s20')
  h1 = net.addHost('h1')
  net.addLink(s5, h1)
  h2 = net.addHost('h2')
  net.addLink(s20, h2)
  h3 = net.addHost('h3')
  net.addLink(s17, h3)
  h4 = net.addHost('h4')
  net.addLink(s10, h4)
  h5 = net.addHost('h5')
  net.addLink(s10, h5)
  h6 = net.addHost('h6')
  net.addLink(s14, h6)
  h7 = net.addHost('h7')
  net.addLink(s13, h7)
  h8 = net.addHost('h8')
  net.addLink(s19, h8)
  h9 = net.addHost('h9')
  net.addLink(s6, h9)
  h10 = net.addHost('h10')
  net.addLink(s19, h10)
  h11 = net.addHost('h11')
  net.addLink(s5, h11)
  h12 = net.addHost('h12')
  net.addLink(s10, h12)
  h13 = net.addHost('h13')
  net.addLink(s17, h13)
  h14 = net.addHost('h14')
  net.addLink(s5, h14)
  h15 = net.addHost('h15')
  net.addLink(s3, h15)
  h16 = net.addHost('h16')
  net.addLink(s12, h16)
  h17 = net.addHost('h17')
  net.addLink(s18, h17)
  h18 = net.addHost('h18')
  net.addLink(s12, h18)
  h19 = net.addHost('h19')
  net.addLink(s2, h19)
  h20 = net.addHost('h20')
  net.addLink(s15, h20)
  net.addLink(s1, s7)
  net.addLink(s2, s15)
  net.addLink(s2, s19)
  net.addLink(s3, s19)
  net.addLink(s5, s8)
  net.addLink(s8, s11)
  net.addLink(s6, s10)
  net.addLink(s6, s16)
  net.addLink(s7, s14)
  net.addLink(s7, s15)
  net.addLink(s9, s12)
  net.addLink(s10, s14)
  net.addLink(s11, s12)
  net.addLink(s11, s18)
  net.addLink(s12, s17)
  net.addLink(s13, s17)
  net.addLink(s16, s17)
  net.addLink(s18, s20)
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
  s11.start([c0])
  s12.start([c0])
  s13.start([c0])
  s14.start([c0])
  s15.start([c0])
  s16.start([c0])
  s17.start([c0])
  s18.start([c0])
  s19.start([c0])
  s20.start([c0])
  CLI( net )
  net.stop()


if __name__ == '__main__':
  setLogLevel( 'info' )
  topology()
