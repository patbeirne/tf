# tf_test  Unit test for Text File manipulations
import tf

# you should have a medium sized file called 'a' in '/'
# and free space equivalent to 2x the size of 'a'

def bench():
  import time
  a=time.ticks_us()
  cp('a','b')
  b=time.ticks_us()
  print("time to copy={}".format((b-a)/1e6))
  input("next")  

  a=time.ticks_us()
  grep('a','kernel')
  b=time.ticks_us()
  print("time to grep={}".format((b-a)/1e6))
  input("next")  

  a=time.ticks_us()
  sed('a','s/kernel\s*/KERNEL /')
  b=time.ticks_us()
  print("time to sed-replace={}".format((b-a)/1e6))
  input("next")  

  os.remove('a.bak')
  a=time.ticks_us()
  cp('b','a')
  b=time.ticks_us()
  print("time to copy={}".format((b-a)/1e6))
  input("next")

  a=time.ticks_us()
  sed('a','100-130x/(PM|AGP):/')
  b=time.ticks_us()
  print("time to sed-extract{}".format((b-a)/1e6))
  input("next")

  a=time.ticks_us()
  cat('b', numbers=True)
  b=time.ticks_us()
  print("time to cat= {}".format((b-a)/1e6))
  input("next")

  os.remove('a.bak')
  cp('b','a')

  a=time.ticks_us()
  sed('a', '100a!! a line of text!!')
  b=time.ticks_us()
  print("time to sed-insert= {}".format((b-a)/1e6))

  os.remove('a.bak')


