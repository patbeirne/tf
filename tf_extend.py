import os,sys,network,socket,time,machine,gc,tf,btree

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
  def __init__(self,nums=False):
    self.i=0
    self.nums=nums
  def write(self,text):
    if self.i==-1: return
    self.i += 1
    if self.nums: sys.stdout.write(str(self.i)+' ')
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
    nums=False
    if cmd=='wc':
      w = wc()
    else:
      if args[1]=='-n':
        nums=True
        del(args[1])
      w = lessor(nums)
    try:
      tf.transfer(args[1],w)
      if cmd=='wc':
        print(f"lines: {w.lines}\twords: {w.words}\tbytes: {w.bytes_}")
    except:
      print("file not found: "+args[1])

  elif cmd in ('ifconfig','ip'):
    ifc=network.WLAN().ifconfig()
    print(f"IP: {ifc[0]}\tmask: {ifc[1]}\tgateway: {ifc[2]}\tDNS: {ifc[3]}")

  elif cmd in ('host','nslookup','dig'):
    if len(args)<2:
      print("syntax: host <domain.name>")
    else:
      try:
        print(f"host <{args[1]}> is at {socket.getaddrinfo(args[1],80)[0][-1][0]}")
      except:
        print("network/DNS not available")

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
      print(f"ch: {i[2]}\tRSSI: {i[3]}\t{"open" if i[4]==0 else ""}\tSSID: {i[0]}")

  elif cmd=='freq':
    # identify esp32 or esp8266
    try:  # is this esp8266
      machine.TouchPad
      freqs=("160","80","240")
    except AttributeError:
      freqs=("160","80")
    if len(args)==1 or args[1] in freqs:
      if len(args)>1:
        machine.freq(int(args[1])*1000000)
      print(f"master cpu frequency {machine.freq()//1000000}MHz")
    else:
      print("syntax: freq [ 160 | 80 | 240 ] ")

  elif cmd=='btree':
    try:
      f=open(args[1])
      b=btree.open(f)
      print("Key\t\tValue")
      i=0
      for k,v in b.items():
        print(f"{k:10}\t{v}")
        i+=1
        if i%30==0:
          r=input("continue? ")
          if r=='n': break
    except OSError:
      print("file not found or is not a btree database")

  elif cmd=='exec':
    try:
      exec(open(args[1]).read(),globals(),globals())
    except OSError:
      print("file not found")
  elif cmd=='free':
    print(f"memory used: {gc.mem_alloc()}\tmemory free:{gc.mem_free()}")
  elif cmd=='help':
    print("==Extended commands")
    print("  connect <essid> <password> \tscan")
    print("  ifconfig/ip        \t\thost/dig/nslookup <domain.name>")
    print("  freq [160 | 80 | 240]\t\texec <python-filename>")
    print("  free        \t\t\twc <filename>")
    print("  less/more [-n] <filename>")
    print("  btree <filename>")
  else: # command not found
    return False
  return True  
