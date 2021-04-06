# tf  Text File manipulations
#   for micropython and other tiny environments 
# (c) Pat Beirne patb@pbeirne.com
import re,os,sys,gc

# ====legend====
# e=end
# f=input file
# g=output file
# i=iteration variable
# m=line range
# r=replace text
# s=start/search/string
# sp=search regex

def transfer(src,dest,first=1,last=0xFFFFFFFF,numbers=False,grep_func=None):
  #src is a filename, dst is a handle
  i=0
  try:
    with open(src) as f:
      for lin in f:
        i=i+1
        if i<first or i>last:
          continue
        if grep_func and not grep_func(lin):
          continue
        if numbers:
          dest.write(str(i)+' ')
        dest.write(lin)
  except:
    print("could not open file {}".format(src))

def cp(src,dest):
  try:
    with open(dest,'w') as g:
      transfer(src,g)
  except:
    print("could not write to file {}".format(dest))

def grep(filename, pattern, numbers=False):
  m=re.compile(pattern)
  if not m:
    print("grep() called with invalid pattern")
    return 
  transfer(filename,sys.stdout,numbers=numbers,grep_func=(lambda x:m.search(x)))

def cat(filename, first=1, last=1000000, numbers=False, title=True):
  if title:
    print("===={}=====".format(filename))
  transfer(filename,sys.stdout,first,last,numbers=numbers)

def sed(filename, sed_cmd, bak_ext=".bak"):
  # parse the sed_cmd
  # group 1,3 are the n-start, n-end    group 4 is command: aidsxX
  a=re.search("^(\d*)([,-](\d+|\$))?\s*([sdaixX].*)",sed_cmd)
  if not a:
    print("sed() failed; 2nd argument must be a number-range followed by one of sdaixX; no changes applied")
    return
  cmd=a.group(4)

  s,e=(1,1000000)
  if a.group(1):
    s=e=int(a.group(1))
  if a.group(3):
    e=1000000 if a.group(3)=='$' else int(a.group(3))

  op=cmd[0]
  if op not in "sdiaxX":
    print("sed requires an operation, one of 's,d,i,a,x or X'")
    return
  #print("sed command parser of <{}> returned {} {} {} {}".format(cmd,sr,de,ins,add))
  if op in "sxX":
    if len(cmd)<2: 
      print("invalid sed argument")
      return
    dl=cmd[1]
    if op=='s':
      gs=re.search("s"+dl+"([^"+dl+"]*)"+dl+"([^"+dl+"]*)"+dl,cmd)
    else:
      gs=re.search("[xX]"+dl+"([^"+dl+"]*)"+dl,cmd)
    if not gs:
      print("invalid sed search pattern")
      return 0,0
    if op=='s':
      ss,r = gs.group(1),gs.group(2)
      #print("search <{}> and replace <{}>".format(s,r))  
    else:
      ss=gs.group(1) 
      #print("search <{}>".format(s))  
    sp=re.compile(ss) 

  extra=a.group(4)[1:] + '\n' 

  try:
    os.rename(filename,filename+bak_ext)
  except:
    print("problem with filename; backup failed; no changes made")
    return

  i=h=0
  try: 
    with open(filename+bak_ext) as f:
      with open(filename,'w') as g:
        for lin in f:
          i=i+1
          m=(i>=s and i<=e)
          if op=='s' and m:
            lin=lin[:-1]
            if sp.search(lin): h+=1
            lin=sp.sub(r,lin)+'\n'
          if op=='d' and m:
            h+=1
            continue   # delete line
          if op=='i' and m:
            #print("insert a line before {} <{}>".format(i,extra))
            g.write(extra)
            h+=1
          if op in "aids":
            g.write(lin)
          elif m and (op=='x' if sp.search(lin) else op=='X'):
            g.write(lin)
            h+=1
          if op=='a' and m:
            #print("append a line after {} <{}>".format(i,extra))       
            g.write(extra)
            h+=1
        #f.write("--file modifed by sed()--\n")
  except OSError:
    print("problem opening file {}".format(filename))
  except RuntimeError:
    print("problem with the regex; try a different pattern")
  return (i, h)

def _dir(d='.'):
  try:  
    for f in os.listdir(d):
      s=os.stat(d+'/'+f)
      print("{}rwx all {:9d} {}".format('d' if (s[0] & 0x4000) else '-',s[6],f))
  except:
    print("not a valid directory")
  s=os.statvfs('/')
  print("disk size:{:8d} KB   disk free: {} KB".format(s[0]*s[2]//1024,s[0]*s[3]//1024))

'''-----cut here if you only need the functions-----'''
def ext_cmd(a):
  return
if 'tf_extend.py' in os.listdir():
  import tf_extend
  ext_cmd=tf_extend.cmd

def _help():
  print("==Simple shell v1.1")
  print("  cp/copy <src-file> <dest-file>")
  print("  mv/move <src-file> <dest-file>    \t\trm/del <file>")
  print("  cd [<folder>]       mkdir <folder>\t\trmdir <folder>")
  print("  dir/ls [<folder>]")
  print("  cat/list [-n] [-l <n>,<m>] <file>")
  print("  grep <pattern> <file>")
  print("  sed <pattern> <file>")
  print("      pattern is '<line-range><op><extra>'   e.g'a/search/replace/', 'x!TODO:!', '43,49d', '8itext'")
  print("      patterns with spaces require single-quotes   sed ops are one of s/d/i/a/x/X")
  print("      sed does not work across line boundaries     sed s/x/X-patterns: non-/ delimiters are allowed")
  print("file names must NOT have embedded spaces           options must be early on the command line")
  ext_cmd('help')

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
  print("Simple shell: cp/copy mv/move rm/del cat/list cd dir/ls mkdir rmdir grep sed help")
  while 1:
    numbers=False
    r=input(os.getcwd()+"$ ")
    rp=r.split()
    if not len(rp): continue
    op=rp[0]
    if op in ('dir','ls'):
      _dir(rp[1] if len(rp)>1 else '.')
    elif op in ('cat','list'):
      n=(" -n " in r) #print line-nums
      s,e=1,1000000 #start/end
      g=re.search("\s(-l\s*(\d+)([-,](\d+|\$)?)?)\s+",r[3:])
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
      r=sed(rp[-1],parseQuotedArgs(r[4:]))
      if r:
        print("Lines processed: {}  Lines modifed: {}".format(*r))
    elif op=='cd':
      os.chdir(rp[1] if len(rp)>1 else '/')
    elif op=='help':
      _help()
      ext_cmd(rp)
    elif ext_cmd(rp):
      pass
    else:
      try:
        if op in ('cp','copy'):
          cp(rp[1],rp[2])
        elif op=='mkdir':
          os.mkdir(rp[1])
        elif op=='rmdir':
          os.rmdir(rp[1])
        elif op in('mv','move'):
          os.rename(rp[1],rp[2])
        elif op in('rm','del'):
          os.remove(rp[1])
        else:
          print("command not implemented")
      except IndexError:
        print("not enough argments; check syntax with 'help'")
      except OSError:
        print("file not found")
    gc.collect()
  
if __name__=="tf":
  print("tf module loaded; members cp(), cat(), cd(), _dir(), grep() and sed()")
  main()


