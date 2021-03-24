# tf  Text File manipulations
#   for micropython and other tiny environments 

#NOTE: the ESP8266 port cannot to \1,\2 type replacements in the s/search/replace/ operator
import re,os,sys,gc

def _file_scan(src,dest,start=1,end=0xFFFFFFFF,numbers=False,grep_func=None):
  #src is a filename, dst is an open handle
  i=0
  try:
    with open(src) as f:
      for line in f:
        i=i+1
        if i<start or i>end:
          continue
        if grep_func and not grep_func(line):
          continue
        if numbers:
          dest.write(str(i)+' ')
        dest.write(line)
  except:
    print("could not open file {}".format(src))

def cp(src_f, dst_f):
  try:
    with open(dst_f,'w') as g:
      _file_scan(src_f,g)
  except:
    print("could not write to file {}".format(dst_f))

def grep(filename, pattern, numbers=False):
  m=re.compile(pattern)
  if not m:
    print("grep() called with invalid pattern")
    return None
  _file_scan(filename,sys.stdout,numbers=numbers,grep_func=(lambda x:m.search(x)))
  print()

def cat(filename, first=1, last=1000000, numbers=False, title=True):
  if title:
    print("===={}=====".format(filename))
  _file_scan(filename,sys.stdout,first,last,numbers=numbers)
  print()

def sed(filename, sed_cmd, bak_ext="bak"):
  #print("sed() called with sed_cmd=<{}>".format(sed_cmd))
  # parse the sed_cmd
  # group 1,3 are the n-start, n-end    group 4 is command
  g=re.search("^(\d*)([,-](\d+|\$))?\s*([sdaixX].*)",sed_cmd)
  if not g:
    print("sed() failed; 2nd argument must be a number followed by one of sdaixX; no changes applied")
    return 0,0
  cmd=g.group(4)
  #print("sed() cmd parsed into <{}>,<{}> and <{}>".format(g.group(1),g.group(3),g.group(4)))

  start,end=(1,1000000)
  if g.group(1):
    start=end=int(g.group(1))
  if g.group(3):
    end=1000000 if g.group(3)=='$' else int(g.group(3))

  op=cmd[0]
  if op not in "sdiaxX":
    print("sed requires an operation, one of 's,d,i,a,x or X'")
    return 0,0
  #print("sed command parser of <{}> returned {} {} {} {}".format(cmd,sr,de,ins,add))
  if op in "sxX" and len(cmd)<2: 
    print("invalid sed argument")
    return (0,0)
  if op=='s':
    dl=cmd[1]
    gs=re.search("s"+dl+"([^"+dl+"]*)"+dl+"([^"+dl+"]*)"+dl,cmd)
    if not gs:
      print("invalid sed search-and-replace pattern")
      return (0,0)
    s,r = gs.group(1),gs.group(2)
    #print("search <{}> and replace <{}>".format(s,r))  
    sp=re.compile(s) 
  if op=='X' or op=='x':
    dl=cmd[1]
    gs=re.search("[xX]"+dl+"([^"+dl+"]*)"+dl,cmd)
    if not gs:
      print("invalid sed search pattern")
      return (0,0)
    sp=re.compile(gs.group(1)) 

  extra=g.group(4)[1:] + '\n' 

  try:
    os.rename(filename,filename+'.'+bak_ext)
  except:
    print("problem with filename; backup failed; no changes made")
    return (0,0)

  i=h=0
  try: 
    with open(filename+'.'+bak_ext) as d:
      with open(filename,'w') as f:
        for lin in d:
          i=i+1
          m=(i>=start and i<=end)
          if op=='s' and m:
            if sp.search(lin): h+=1
            lin=sp.sub(r,lin)
          if op=='d' and m:
            h+=1
            continue   # delete line
          if op=='i' and m:
            #print("insert a line before {} <{}>".format(i,extra))
            f.write(extra)
            h+=1
          if op in "aids":
            f.write(lin)
          elif (m and (op=='x' and sp.search(lin)) or (op=='X' and not sp.search(lin))):
            f.write(lin)
            h+=1
          if op=='a' and m:
            #print("append a line after {} <{}>".format(i,extra))       
            f.write(extra)
            h+=1
        #f.write("--file modifed by sed()--\n")
  except OSError:
    print("problem opening file {}".format(filename))
  except RuntimeError:
    print("problem with the regex; try a different pattern")
  return (i, h)

def _dir(d=''):
  try:  
    for g in os.listdir(d):
      s=os.stat(d+'/'+g)
      print("{}rwx all {:9d} {}".format('d' if (s[0] & 0x4000) else '-',s[6],g))
  except:
    print("not a valid directory")
  s=os.statvfs('/')
  print("disk size:{:8d} KB   disk free: {} KB".format(s[0]*s[2]//1024,s[0]*s[3]//1024))


'''-----cut here if you only need the above functions-----'''
def _help():
  print("simple shell v1.0")
  print("  cp/copy <src-file> <dest-file>")
  print("  mv/move <src-file> <dest-file>           rm/del <file>")
  print("  cd [<folder>]       mkdir <folder>       rmdir <folder>")
  print("  dir/ls [<folder>]")
  print("  cat/list [-n] [-l <n>,<m>] <file>")
  print("  grep <pattern> <file>")
  print("  sed <pattern> <file>")
  print("          where <pattern> is '[<n>,<m>] s/search/replace/' or '<n>[,<m>]d' or '<n>i<text>' or '<n>a<text' ")
  print("file names must NOT have embedded spaces               options must be early on the command line")
  print("search patterns with spaces require single-quotes      sed implements s/d/i/a/x/X")
  print("sed does not work across line boundaries               sed s-patterns: non-/ delimiters are allowed")

def parseQuotedArgs(st):
  if st[0]=="'":
    p=re.search("'((\'|[^'])*)'",st)
    if not p:
      print("quoted pattern error")
      return ""
    return p.group(1)
  else:
    return st.split()[0]

def main():
  print("simple shell: cp/copy mv/move rm/del cat/list cd dir/ls mkdir rmdir grep sed help")
  while 1:
    numbers=False
    r=input(os.getcwd()+"$ ")
    rp=r.split()
    if not len(rp): continue
    op=rp[0]
    if op=='dir' or op=='ls':
      _dir(rp[1] if len(rp)>1 else '')
    elif op=='cat' or op=='list':
      n=(" -n " in r) #print line-nums
      s,e=(1,1000000) #start/end
      g=re.search("\s+(-l\s*(\d+)([-,](\d+|\$)?)?)\s+",r[3:])
      if g:
        s=e=int(g.group(2))
        if g.group(3):
	      e=int(g.group(4)) if g.group(4) and g.group(4).isdigit() else 1000000
      cat(rp[-1],s,e,numbers=n)
    elif op=='grep':
      if len(rp)<3:
        print("grep pattern filename") 
        continue
      grep(rp[-1],parseQuotedArgs(r[5:]),numbers=True)
    elif op=='sed':
      if len(rp)<3:
        print("sed pattern filename")
        continue
      lines, hits = sed(rp[-1],parseQuotedArgs(r[4:]))
      print("Lines processed: {}  Lines modifed: {}".format(lines, hits))
    elif op=='cd':
      os.chdir(rp[1] if len(rp)>1 else '/')
    elif op=='help':
      _help()
    else:
      try:
        if op=='cp' or op=='copy':
          cp(rp[1],rp[2])
        elif op=='mkdir':
          os.mkdir(rp[1])
        elif op=='rmdir':
          os.rmdir(rp[1])
        elif op=='mv' or op=='move':
          os.rename(rp[1],rp[2])
        elif op=='rm' or op=='del':
          os.remove(rp[1])
        else:
          print("command not implemented")
      except IndexError:
        print("not enough argments; check syntax")
      except OSError:
        print("file not found")
    gc.collect()
  
if __name__=="tf":
  print("tf module loaded; members cp(), cat(), cd(), _dir(), grep() and sed()")
  main()


