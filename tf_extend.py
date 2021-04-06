import os,network,socket,time,machine,gc
def cmd(args):
  if args[0]=='ifconfig':
    ifc=network.WLAN().ifconfig()
    print("IP: {}\tmask: {}\tgateway: {}\tDNS: {}".format(*ifc))
    return True
  elif args[0]=='host':
    if len(args)<2:
      print("syntax: host <domain.name>")
      return False
    print("host <{}> is at {}".format(args[1],socket.getaddrinfo(args[1],80)[0][-1][0]))
    return True
  elif args[0]=='connect':
    if len(args)<3:
      print("syntax: connect <ssid> <password>")
      return False
    w=network.WLAN(network.STA_IF)
    w.connect(args[1],args[2])
    print("connecting...",end=' ')
    time.sleep(3)
    print(w.ifconfig() if w.isconnected() else "not yet connected; try 'ifconfig' in a few seconds")
    return True
  elif args[0]=='scan':
    w=network.WLAN(network.STA_IF)
    print("scanning...")
    s=w.scan()
    if len(s)==0:
      print("no AP found")
      return True
    for i in s:
      print("ch: {}\tRSSI: {}\t{}\tSSID: {}".format(i[2],i[3],"open" if i[4]==0 else "",i[0]))
    return True
  elif args[0]=='freq':
    if len(args)==1 or args[1] in ("160","80"):
      if len(args)>1:
        machine.freq(int(args[1])*1000000)
      print("master cpu frequency {}MHz".format(machine.freq()//1000000))
    else:
      print("syntax: freq [ 160 | 80 ]")
    return True
  elif args[0]=='exec':
    if len(args)<2:
      print("syntax: exec <python-filename>")
    else:
      try:
        exec(open(args[1]).read(),globals(),globals())
      except OSError:
        print("file not found")
    return True
  elif args[0]=='free':
    print("memory used: {}\tmemory free:{}".format(gc.mem_alloc(),gc.mem_free()))
    return True
  elif args[0]=='help':
    print("==Extended commands")
    print("  connect <essid> <password> \tscan")
    print("  ifconfig                   \thost <domain.name>")
    print("  freq [ 160 | 80 ]          \texec <python-filename>")
    print("  free")
    return True
  else:
    return False

