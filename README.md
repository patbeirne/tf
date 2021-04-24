# TF

A module for manipulating **T**ext **F**iles in the *MicroPython* environment.  

[TOC]

#### TL;DR
A small app for the *MicroPython* board environment, to allow easy access to text files stored in the local flash file system.

## Oveview

I discovered *MicroPython* when working on the ESP8266 processor. Everything seemed very nice, except it was awkward moving files around. All the methods I could find required a back-and-forth with the programmer's desktop.

This **TF** module simulates a command shell and gives you the ability to copy, move and delete files. It includes commands for searching, editing and making backups of local text files, using only the embedded processor. The module itself is small (about 7k) and can be downloaded into the target machine. Once there, the user can invoke the command line, or simply call the functions from Python.

For example, to make a backup of a file from your Python app, you can call  

```
    tf.cp('log.txt','log.2021-03-20.bak')
```

or you can use the builtin command line and

```
/$ cp mail.log m.log.bak
/$ dir
-rwx all       230 boot.py
-rwx all      2886 m.log.bak
-rwx all      2886 mail.log
-rwx all      2401 main.py
-rwx all      2259 main_test.py
-rwx all     99182 mqtt.log
-rwx all      6949 tf.py
-rwx all        15 webrepl_cfg.py
disk size:     392 KB   disk free: 196 KB

/$ cat -n -l 1000-1005 mqtt.log
====mqtt.log=====
1000 1616120701: Client mosq-d911rjWHX3Rdwcntoo disconnected.
1001 1616124181: New connection from 72.53.209.21 on port 1883.
1002 1616124181: New client connected from 72.53.209.21 as mosq-kwcmiGmZ7jlEVRecrU (c1, k60).
1003 1616124181: Client mosq-kwcmiGmZ7jlEVRecrU disconnected.
1004 1616126374: Socket error on client DVES_98843E, disconnecting.
1005 1616126425: Client DVES_83244E has exceeded timeout, disconnecting.

/$ grep 24.114.80.\d+ mqtt.log
977 1616120273: New connection from 24.114.80.91 on port 1883.
980 1616120273: New client connected from 24.114.80.91 as Rutherford1616120233590 (c1, k60, u'patb').
1046 1616142039: New connection from 24.114.80.109 on port 1883.
1049 1616142039: New client connected from 24.114.80.109 as Rutherford1616120233590 (c1, k60, u'patb').

/$ 
```
Uses:

* make a backup copy of a file
* examine and clean up your filesystem and its directories
* scan a mega-byte log file for entries using the `grep`(search) or `sed` (search-and-extract) methods
* make small changes to your Python files (change parameters, add notes, etc)

The first half of the **TF** module holds the functions. You can use these as functions within your own Python code. The functions are documented at the bottom of this README.

The second half of the module's code contains the simple command shell. [If you don't need the shell, just delete everything from `-----cut here` downward.]


## Simple Command Line

By invoking `tf.main()`, you will be presented a command prompt, similar to Linux, where the prompt shows you what directory/folder you are currently in, and a '$'. 

From there, you can enter one of these commands:

```
cp    <src-file> <dest-file>  
mv    <src-file> <dest-file>
rm    <filename>

dir   [<dir name>]
cd    [<dest dir>]
mkdir <dirname>
rmdir <dirname>

cat   [-n] [-l<n>-<m>] <filename>
grep  <pattern> <filename>
sed   <pattern> <filename>

help
```

You can use synonyms for these: `copy = cp`, `move = rename = mv`, `del = rm`, `list = cat`, `ls = dir`. The `mv/move/rename` can rename directories. 

For the `cat/list` command, you can enable line numbers with `-n` and you can limit the display range with `-l n-m` where `n` and `m` are decimal numbers (and n should be less than m). These are all valid uses of `cat`

```
cat -n log.txt             # whole file
cat -n -l223 log.txt       # one line  
cat -l 223-239 log.txt     # 17 lines
cat -l244-$ log.txt        # from 244 to the end
```

For `grep`  and `sed`, the patterns are *MicroPython* regular explressions, from the `re` module. If a pattern has a space character in it, then the pattern **must** be wrapped in  single-quote ' characters; patterns without an embedded space char can simply be typed. [The line parser is basically a `str.split()` unless a leading ' is detected.] To include a single quote in a quoted-pattern, you can escape it with ``\'` .

The documentation for the `sed` command is [here](#sed())

Here are some valid uses of `sed` and `grep`

```text
grep #define main.c
grep '^\s*#define\s+[A-Z]' main.c
sed 1,100s/recieve/receive/g doc.txt
sed '33-$s/it is/it\'s/g' doc.txt
sed '45i   a new line of indented text' doc.txt
```

The **REPL** typing-history is functional, so you can use the up-arrow to recall the last 4-5 commands. Use the left-arrow and backspace to correct lines that have errors.

Commands with invalid syntax return a line of information, and are ignored. Non valid commands are simply eaten and ignored.

## Limitations

In its present form, the module has these limitations:  

* filenames are limited to 255 chars
* file contents must be text
	* or have a `\n` at least every 4096 characters
	* `sed()` requires lines <=2048 characters, and this `sed()` won't match binary chars
* in the simple shell
  * filenames must not have spaces
  * patterns with spaces ***must*** be quoted
  * the target of `cp` and `mv` *cannot* be a simple a directory-name as in Linux; write the whole filename *w.r.t,* the current directory
* for the `sed` function and command, the 
[search](https://docs.micropython.org/en/latest/library/ure.html) pattern can have wildcards like ``\s`, `\w` and `\d`. The replace pattern cannot have *any* of these, and can only have `\0`, `\1`, etc
  * search patterns involving \ escapes other than those and `\'` probably won't work
* the complexity of pattern matching is limited. 
  * try to format the grep patterns so they avoid deep stack recursion. For example, `([^#]|\\#)\s*` has a very generous search term as the first half, and can cause deep-stack recursion. The equivalent `(\\#|[^#])\s*` is more likely to succeed.
* with `sed`, lines are parsed and saved one-line-at-a-time, so pattern matching to `\n` and `\r` does not work; `sed` cannot work over line boundaries
* this simple shell is different than [`mpfshell`](https://github.com/wendlers/mpfshell) in that *this* shell runs entirely on the target device. There is no allowance in this shell for transferring files in/out of the target.
* after a restart of your *MicroPython* board, you can invoke the shell with `import tf`; if you `^C` out of the shell, the second invocation of `tf` will have to be `import tf` followed by `tf.main()`, since the python interpreter caches the module and only loads it once per restart; you can intentionally restart the REPL prompt by hitting `^D` 
 
## Examples

Make a simple change to a source file, perhaps modify a constant.

```
[command line]  
   /$ grep CITY main.py
   58 CITY_NAME = 'Toronto'
   /$ sed '58s/CITY_NAME = \'Toronto\'/CITY_NAME = \'Ottawa\'/' main.py  
   /$ sed 58s/Toronto/Ottawa/ main.py
[python function]  
   tf.sed('main.py','10-30s/CITY_NAME = \'Toronto\'/CITY_NAME     = \'Ottawa\'/')  
```

Remove some comments from a source file.

```
[command line]
   /$ sed X/^#\s*TODO:/ main.py
[python function]
   tf.sed('main.py','X/^#\s*TODO:/')
```

Search a log file for an incident

```
[command line]
   /$ grep [Ee]rror log.txt
   /$ grep '2021-02-12 16:\d\d' log.txt
   
   # search and keep a record
   /$ cp log.txt log.details
   /$ sed 'x/2021-02-12 16:\d\d` log.details

[python function]
   tf.grep('log.txt','^2021-02-12 16:\d\d',numbers=True)
```

## Installation

~If you need help with getting connected to your *MicroPython* board, there are excellent howto guides here and here~ TODO! 

Move the 'tf.py' file over to the target. You can use `webrepl` [command line program](https://github.com/micropython/webrepl)  or the **WEBREPL** [web page](http://micropython.org/webrepl/) .  If you want the command line extensions, then send over the `tf_extend.py` file as well

Once the module is present in the file system of the target, you can use the **REPL** command line interface to invoke it

```
 >>> import tf
tf module loaded; members cp(), cat(), _dir(), grep() and sed()
simple shell: cp/copy mv/move rm/del cat/list cd dir/ls mkdir rmdir grep sed help
/$ 
```

This is the *simple command line*. You can type `dir` to get an idea of what's already in your flash file system, and `cat` to see the contents. [You'll probably find the files `boot.py` and `webrepl_cfg.py` are already installed]

```
  /$ dir
 -rwx all       230 boot.py
 -rwx all      2886 mail.log
 -rwx all      2401 main.py
 -rwx all      2259 main_test.py
 -rwx all     99182 mqtt.log
 -rwx all        98 test.py
 drwx all         2 test_dir
 -rwx all      6903 tf.py
 -rwx all        15 webrepl_cfg.py
 disk size:     392 KB   disk free: 212 KB
 /$ cd test_dir
 /test_dir$ dir
 -rwx all        98 test.py
 disk size:     392 KB   disk free: 212 KB
 /test_dir$ 
```

If you don't need the *simple command line*, you can still use the methods listed at the bototm of this readme. Feel free to cut the `tf.py` module in half by deleting everything below the line

```
  -----cut here
```

## Extensions

I found the simple command line so useful, I added some extra non-file-related functions. These are included in the optional file `tf_extend.py`.  The available command list is extended to include

```
scan                      # scan and show the local AP's
connect essid password    # create a persistent wifi connection
ifconfig                  # show current ip address
host <domain.name>        # do an DNS lookup
freq [160 | 80]           # get/set the ESP8266 frequency
exec <python-filename>    # execute a small python file
free                      # display the heap size: used + free
wc <filename>             # display the line count, word count and bytes
less/more [-n] <filename> # similar to cat, but displays 30 lines at a time
```
Synonyms: `ip = ifconfig`, `more = less`, `dig = nslookup = host`

The `tf.py` module checks to see if the `tf_extend.py` files exists, and forwards unknown commands to it. The `help` system also extends when the extension file exists.

Installing the extensions module uses about 3k of flash/disk space and 4kB of heap ram.

## Performance

Typical performance on an ESP8266 @80MHz, 90kB log file, 1200 lines; serial connected terminal @115200baud

| operation            | time     | bytes/sec      |
| --------------------:| --------:| --------------:|
| copy                 | 5.7 s    | 16kB/s         |
| cat                  | 8.3 s    | 10.8kB/s       |
| grep                 | 7.5s     | 12kB/s         |
| sed-append           | 6.4s     | 14KB/s         |
| sed-search/replace   | 8.0-8.2s | 11.0-11.25kB/s |
| sed-extract 30 lines | 2.5s     | 36kB/s         |

**Note**: The copy() time is indicative of the flash-write speed. The grep() and cat() speeds are indicative of the serial rate, as all the characters must be sent through the UART at 115kbaud=11.5kB/s. The sed-extract() is faster, because it only writes 30 lines of text to the flash. The sed-append() is constrained by having to write the entire file.



## Functions

If you don't need the command line, you're welcome to just use the functions provided by the **tf** module. You would typically invoke the as members of tf: 

```
import tf
try:
  tf.cp("log.txt","log.bak")
except:
  print("problem copying file")
```

#### cp()

```
   cp(src-filename, dest-filename)
   in: src-filename    file to read
       dest-filename   file to write
   returns: Null
   except: OSError if src or dest file cannot be found/created
```

Simply copies a source file to a destination file. Filenames may include folders or . or .. prefixes; use `/` to separate folder+filename. The destination is overwritten if it exists. This function reads-&-writes one line at a time, so it can handle megabyte files. Typical speeds are 100kB/sec on an ESP8266. 

**NOTE** this function *only works on text files* delimited by `\n`. Line lengths of up to 4096 work fine on the ESP8266.

#### cat()

```
    cat(filename, first=1, last=1000000, numbers=False, title=True)
    in: filename    file to read and display
        first       the first line to display
        last        the last line to display
        numbers     whether to prepend each line with line-number + space
        title       whether to prepend the listing with the filename
    return: Null
    except: OSError if file cannot be found
```

Displays the source file on the screen.  You can specify a line range, and whether line numbers are displayed, and whether to put a *title line* on the output display.  

#### _dir()

```
    dir(directory-name='.')
    in:     directory-name     defaults to current directory
    return: Null
    except: OSError if directory doesn't exist
```

Displays the contents of the current working directory. Files and folders are marked; ownership is assumed to be `all` and all are assumed to be `rwx` (read+write+execute). The file size is also shown and the disk size summary is shown at the bottom. 

File dates are not displayed, as they all depend on the time from last reboot, and don't mean much in this environment.

NOTE: the name is `_dir()` because `dir()` is a python builtin.

#### grep()

```
    grep(filename, pattern, numbers=False)
    in:  filename         the file to scan
         pattern          a python regex to match
         numbers          whether to prepend a line-number + space 
    return: Null
    except: ValueError if the pattern fails to compile as reg-ex
        OSError if the file cannot be found
        RunTimeError if the reg-ex parsing uses up all the memory
```

You can search a file for a pattern, and any matching lines are displayed. Searches are restricted to within a line, don't bother with `\r` and `\n` searches. 

 
###### Examples

```
tf.grep('log.txt', '2021-03-\d\d')
tf.grep('config.txt', '^user\s*=')
tf.grep('config.ini', '\[\w*\]', numbers = True)
```

#### sed()

```
  sed(filename, pattern, bak_ext=".bak")
  in:  filename       the file to edit
       pattern        a sed pattern, involving one of "aidsxX"
       bak_ext        the extension to use when creating the file backup (with the dot)
  return: tuple(number of lines in the input file, number of lines modified/added/deleted/matched)
  except: OSError     the file cannot be found, or the backup cannot be created
     ValueError       the reg-ex pattern fails to compile
     RunTimeError     the reg-ex parsing uses up all the memory
```

The *sed()* function is an inline file editor, based on `sed` from the Unix world. When invoked, it first renames the source file to have a `.bak` extension. That file is opened and each line of the source file is loaded in, and a regex pattern match is performed. If the line is changed/found/inserted, then the output is streamed to the new (output) file with the same name as the original; it appears to the user that the files is edited-in-place, with a .bak file created. 

This version of `sed` has 6 commands:

* a appends a line
* i inserts a line
* d deletes a line or lines
* s does a search and replace
* x does a grep and only saves lines that match
* X does a grep and only saves lines that do not match

If the single-letter command is preceded by a number or number-range, then the edit operation only applies to that line(s). A number range may be separated by `-` hyphen or `,` comma. Use `$` to indicate end-of-file.

##### Examples

```
12aMAX_FILE_NAME=255             insert a line AFTER line 12
12iDEFAULT_DIR = "/"             insert a line BEFORE line 12
43-45d                           delete lines 43, 44 and 45
1,20s/^#\s*/##  /                only in lines 1 through 20, replace lines that 
                                 start with a # followed by whitespace
                                 with two-# and two-spaces....to align some comments
```

The `i/a/d` commands should be preceeded by a line number, or range; `sed()` will *insert*, *append* or *delete* once for each line in the range. 
 
The ``x/X` patterns are wrapped in a pair of delimiter characters, typically `/`, although almost any other character is allowed other than space or one of `\^$()[]`. Valid X commands are:

```
x/abcd/
10-20X/\w*\s*\d\d/
x!ratio x/y!
```

Similarly, the s patterns are wrapped in a triplet of delimiter characters, typcially / also. If the search pattern has `()` groups, the replace pattern can refer to them with ``\1 \2`,etc. The /search/replace/ pattern may have a  `g` suffix, to replace replaces multiple occurrences on a line. Valid 's' commands are

```
s/toronto/Toronto/
s/thier/their/g
120-$s/while\s*(True|False)/while 1/
s@ratio\s*=\s*num/denom@ratio = num/denom if denom else 0@
```

**Note**: The function version of sed() can have embedded space characters in the pattern; the command line version (above) requires single-quotes around patterns that have space characters.

**Note**: You will need some free space on your disk, the same size as the source file, as a backup file is *always* made. To edit an 800k file, you should have 800k of free space.

**Note**: `sed()` errors may leave the subject-file empty, but it almost always make the backup file before failing.

#### General Notes

**Note**: On error, all the functions above throw exceptions. The simple command line shell above catches the exceptions. If you use the functions, wrap them up in `try/except`.

**Note**: The functions for

* file delete (`rm, del`)
* file move (`mv, move, rename`)
* change/make/delete directory/folder (`chdir, mkdir, rmdir`)

are not included in this list, because the `os` module already has functions that implement these directly: `os.remove(), os.rename(), os.chdir(), os.mkdir(), os.rmdir()`