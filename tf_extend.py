import os,sys,network,socket,time,machine,gc,tf

# these helper classes let us use the tf.transfer() iterator,
# by intercepting the .write()
class wc():
  def __init__(self):
    self.words=self.lines=self.bytes_=0
  def write(self,text):
    self.bytes_ += len(text)
    self.lines += 1
    self.words += len(text.split())

class lessor():
  def __init__(self):
    self.i=0
  def write(self,text):
    if self.i==-1: return
    self.i += 1
    sys.stdout.write(text)
    if self.i%30==0:
      sys.stdout.write("====> press <enter> to see more, N or Q to quit <====\n")
      g=sys.stdin.read(1)
      if g=='\n': g=sys.stdin.read(1)
      if g in "nNqQ":
        self.i=-1

# the main entry point for the extension
# returns True if the command was interpreted
def cmd(args):
  cmd=args[0]
  if cmd in ('wc','more','less','exec') and len(args)<2:
    print("syntax: "+cmd+" <filename>")
    return True

  if cmd in ('wc','more','less'):
    if cmd=='wc':
      w = wc()
    else:
      w = lessor()
    try:
      tf.transfer(args[1],w)
      if cmd=='wc':
        print("lines: {}\twords: {}\tbytes: {}".format(w.lines, w.words, w.bytes_))
    except:
      print("file not found: "+args[1])

  elif cmd in ('ifconfig','ip'):
    ifc=network.WLAN().ifconfig()
    print("IP: {}\tmask: {}\tgateway: {}\tDNS: {}".format(*ifc))

  elif cmd in ('host','nslookup','dig'):
    if len(args)<2:
      print("syntax: host <domain.name>")
    else:
      print("host <{}> is at {}".format(args[1],socket.getaddrinfo(args[1],80)[0][-1][0]))

  elif cmd=='connect':
    if len(args)<3:
      print("syntax: connect <ssid> <password>")
    else:
      w=network.WLAN(network.STA_IF)
      w.connect(args[1],args[2])
      print("connecting...",end=' ')
      time.sleep(3)
      print(w.ifconfig() if w.isconnected() else "not yet connected; try 'ifconfig' in a few seconds")

  elif cmd=='scan':
    w=network.WLAN(network.STA_IF)
    print("scanning...")
    s=w.scan()
    if len(s)==0:
      print("no AP found")
      return True
    for i in s:
      print("ch: {}\tRSSI: {}\t{}\tSSID: {}".format(i[2],i[3],"open" if i[4]==0 else "",i[0]))

  elif cmd=='freq':
    if len(args)==1 or args[1] in ("160","80"):
      if len(args)>1:
        machine.freq(int(args[1])*1000000)
      print("master cpu frequency {}MHz".format(machine.freq()//1000000))
    else:
      print("syntax: freq [ 160 | 80 ]")

  elif cmd=='exec':
    try:
      exec(open(args[1]).read(),globals(),globals())
    except OSError:
      print("file not found")
  elif cmd=='free':
    print("memory used: {}\tmemory free:{}".format(gc.mem_alloc(),gc.mem_free()))
  elif cmd=='help':
    print("==Extended commands")
    print("  connect <essid> <password> \tscan")
    print("  ifconfig/ip        \t\thost/dig/nslookup <domain.name>")
    print("  freq [ 160 | 80 ]  \t\texec <python-filename>")
    print("  free        \t\t\twc <filename>")
    print("  less/more <filename>")
  else: # command not found
    return False
  return True  
