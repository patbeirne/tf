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

def cp(src,dest):
  with open(dest,'w') as g:
    transfer(src,g)

def cat(filename, first=1, last=1000000, numbers=False, title=True):
  if title:
    print("===={}====".format(filename))
  transfer(filename,sys.stdout,first,last,numbers=numbers)

def grep(filename, pattern, numbers=False):
  m=re.compile(pattern)
  transfer(filename,sys.stdout,numbers=numbers,grep_func=(lambda x:m.search(x[:-1])))

def sed(filename, sed_cmd, bak_ext=".bak"):
  # parse the sed_cmd
  # group 1,3 are the n-start, n-end    group 4 is command: aidsxX
  a=re.search("^(\d*)([,-](\d+|\$))?\s*([sdaixX])(.*)",sed_cmd)
  if not a:
    raise ValueError("sed() failed; pattern must be a number-range followed by one of sdaixX; no changes applied")
  op,args=a.group(4),a.group(5)

  s,e=1,1000000
  if a.group(1):
    s=e=int(a.group(1))
  if a.group(3):
    e=1000000 if a.group(3)=='$' else int(a.group(3))

  if op in "aid" and e-s==1000000:
    raise ValueError("sed(a/i/d) should have a line number")
  #print("sed command parser of <{}> returned {} {} {}".format(op,cmd,a.group(1),a.group(3)))
  if op in "sxX":
    if len(args)<2 or args[0] in "\^$()[]": 
      raise ValueError("invalid sed argument: "+op+args)
    dl=args[0]
    if op=='s':
      gs=re.search(dl+"([^"+dl+"]*)"+dl+"([^"+dl+"]*)"+dl+"(g)?",args)
    else:
      gs=re.search(dl+"([^"+dl+"]*)"+dl,args)
    if not gs:
      raise ValueError("invalid sed search pattern: "+op+args)
    ss=gs.group(1)
    if op=='s':
      r=gs.group(2)
      rm=0 if gs.group(3) else 1
    sp=re.compile(ss) 

  args=args + '\n' 

  try:
    os.rename(filename,filename+bak_ext)
  except:
    raise OSError("problem with filename",filename,"   backup failed; no changes made") 

  i=h=0
  with open(filename+bak_ext) as f:
    with open(filename,'w') as g:
      for lin in f:
        i=i+1
        m=(i>=s and i<=e)
        if op=='s' and m:
          lin=lin[:-1]
          if sp.search(lin): h+=1
          lin=sp.sub(r,lin,rm)+'\n'
        if op=='d' and m:
          h+=1
          continue   # delete line
        if op=='i' and m:
          #print("insert a line before {} <{}>".format(i,extra))
          g.write(args)
          h+=1
        if op in "aids":
          g.write(lin)
        elif m and (op=='x' if sp.search(lin) else op=='X'):
          g.write(lin)
          h+=1
        if op=='a' and m:
          #print("append a line after {} <{}>".format(i,extra))       
          g.write(args)
          h+=1
      #f.write("--file modifed by sed()--\n")
  return (i, h)

def _dir(d='.'):
  for f in os.listdir(d):
    s=os.stat(d+'/'+f)
    print("{}rwx all {:9d} {}".format('d' if (s[0] & 0x4000) else '-',s[6],f))
  s=os.statvfs('/')
  print("disk size:{:8d} KB   disk free: {} KB".format(s[0]*s[2]//1024,s[0]*s[3]//1024))

'''-----cut here if you only need the functions-----'''
def ext_cmd(a):
  return
if 'tf_extend.py' in os.listdir():
  import tf_extend
  ext_cmd=tf_extend.cmd

def _help():
  print("==Simple shell v1.2 for Text Files")
  print("  cp/copy <src-file> <dest-file>")
  print("  mv/move <src-file> <dest-file>    \t\trm/del <file>")
  print("  cd [<folder>]\t\tmkdir <folder>\t\trmdir <folder>")
  print("  dir/ls [<folder>]")
  print("  cat/list [-n] [-l <n>,<m>] <file>")
  print("  grep <pattern> <file>")
  print("  sed <pattern> <file>")
  print("      pattern is <line-range><op><extra>   e.g'a/search/replace/', 'x!TODO:!', '43,49d', '8itext'")
  print("      patterns with spaces require '-quotes\tsed ops are one of s/d/i/a/x/X")
  print("      sed cannot cross line boundaries\t\tsed s/x/X-patterns: non-/ delimiters are ok")
  print("file names must NOT have embedded spaces\toptions must be early on the command line")
  ext_cmd('help')

def parseQuotedArgs(st):
  #returns (pattern,file)
  st=st.strip()  
  if st[0]=="'":
    p=re.search("'(.*?[^\\\\])'\s*(\S*)",st)
    if not p:
      print("error in quoted pattern:",st)
      return 
    return p.group(1),p.group(2)
  else:
    return st.split(None,1)

def main():
  print("Simple shell: cp/copy mv/move rm/del cat/list cd dir/ls mkdir rmdir grep sed help")
  while 1:
    numbers=False
    r=input(os.getcwd()+"$ ")
    rp=r.split()
    if not len(rp): continue
    op=rp[0]
    if op in ('dir','ls'):
      try:
        _dir(rp[1] if len(rp)>1 else '.')
      except:
        print("directory not found")
    elif op in ('cat','list'):
      n=(" -n " in r) #print line-nums
      s,e=1,1000000 #start/end
      g=re.search("\s(-l\s*(\d+)([-,](\d+|\$)?)?)\s+",r[3:])
      if g:
        s=e=int(g.group(2))
        if g.group(3):
          e=int(g.group(4)) if g.group(4) and g.group(4).isdigit() else 1000000
      try:
        cat(rp[-1],s,e,numbers=n)
      except:
        print("file not found",rp[-1])
    elif op in('grep','sed'):
      if len(rp)<3:
        print(op,"pattern filename") 
        continue
      p=parseQuotedArgs(r[4:])
      if not p:
        continue
      try:
        if op=='grep':
          grep(p[1],p[0],numbers=True)
        else:
          r=sed(p[1],p[0])
          if r:
            print("Lines processed: {}  Lines modifed: {}".format(*r))
      except (ValueError, OSError) as e:
        print(e)
      except RuntimeError:
        print("problem with the regex; try a different pattern")
    elif op=='help':
      _help()
      ext_cmd(rp)
    elif ext_cmd(rp):
      pass
    else:
      try:
        if op in ('cp','copy'):
          cp(rp[1],rp[2])
        elif op=='cd':
          os.chdir(rp[1] if len(rp)>1 else '/')
        elif op=='mkdir':
          os.mkdir(rp[1])
        elif op=='rmdir':
          os.rmdir(rp[1])
        elif op in('mv','move'):
          os.rename(rp[1],rp[2])
        elif op in('rm','del'):
          os.remove(rp[1])
        else:
          print("command not implemented:",op)
      except IndexError:
        print("not enough argments; check syntax with 'help'")
      except OSError:
        print("file/folder not found or cannot be written")
    gc.collect()
  
if __name__=="tf":
  print("tf module loaded; members cp(), cat(), _dir(), grep() and sed()")
  main()

# grep 12.*\) dmesg fails
