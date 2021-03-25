# TF

A module for manipulating files in the *MicroPython* environment.  

## Oveview

I discovered *MicroPython* when working on the ESP8266 processor. Everything seemed very nice, except it was awkward moving files around. All the methods I could find required a back-and-forth with the programmer's desktop.

This **TF** module includes functions for creating, searching, editing and making backups of local files, using only the embedded processor. The module itself is small (about 7k) and can be downloaded into the target machine. Once there, the user can invoke it by either calling functions, or using the builtin command line. 

For example, to make a backup, you can call  

```
    tf.cp('log.txt','log.2021-03-20.bak')
```

or you can use the builtin command line and

```
/$ cp m.log.bak mail.log
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

/$ sed x/24\.114\.80/ mqtt.log
Lines processed: 1415  Lines modifed: 4
/$ cat -n mqtt.log
====mqtt.log=====
1 1616120273: New connection from 24.114.80.91 on port 1883.
2 1616120273: New client connected from 24.114.80.91 as Rutherford1616120233590 (c1, k60, u'patb').
3 1616142039: New connection from 24.114.80.109 on port 1883.
4 1616142039: New client connected from 24.114.80.109 as Rutherford1616120233590 (c1, k60, u'patb').

/$ 
```

The first half of the **TF** module holds the functions. These may come in handy for parsing files, making backups or searching through files. 

The second half contains the simple command shell. This may come in handy for testing the functions, experimenting with their functions, or if you, like me, like to play around with a live system. If you don't need the shell, just delete everything from `def _help():` downward.

## Functions

These methods all belong to the **tf** module, so you would typically invoke the as members of tf: 

```
import tf
tf.cp('log.txt','log.bak')`
```

#### cp()

```
   cp(src-filename, dest-filename)
   in: src-filename    file to read
       dest-filename   file to write
   returns: Null
```

Simply copies a source file to a destination file. Filenames may include folders or . or .. prefixes. The destination is overwritten if it exists. This function reads-&-writes one line at a time, so it can handle megabyte files. Typical speeds are 100kB/sec on an ESP8266.

#### cat()

```
    cat(filename, first=1, last=1000000, numbers=False, title=True)
    in: filename    file to read and display
        first       the first line to display
        last        the last line to display
        numbers     whether to prepend each line with line-number + space
        title       whether to prepend the listing with the filename
    return: Null
```

Displays the source file on the screen.  You can specify a line range, and whether line numbers are displayed, and whether to put a *title line* on the output display.  

#### _dir()

```
    dir(directory-name='')
    in:     directory-name     defaults to current directory
    return: Null
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
```

You can search a file for a pattern, and any matching lines are displayed. 

Searches using ^ (start of line) work fine, but searches with $ (end-of-line) aren't currently working.

###### Examples

```
tf.grep('log.txt', '2021-03-\d\d')
tf.grep('config.txt', 'user.\s=')
tf.grep('config.ini', '\[\w*\]', numbers = True)
```

#### sed()

```
  sed(filename, pattern, bak_ext="bak")
  in:  filename       the file to edit
       pattern        a sed pattern, involving one of "aidsxX"
       bak_ext        the extension to use when creating the file backup (without the dot)
  return: tuple(number of lines in the input file, number of lines modified/added/deleted/matched)
```

The *sed* function is an inline file editor, based on `sed` from the Unix world. When invoked, it first renames the source file to have a `.bak` extension. That file is opened and each line of the source file is loaded in, and a regex pattern match is performed. If the line is changed/found/inserted, then the output is streamed to the new (output) file with the same name as the original; it appears to the user that the files is edited-in-place, with a .bak file created. 

This version of `sed` has 6 commands:

* a appends a line
* i inserts a line
* d deletes a line or lines
* s does a search and replace
* x does a grep and only saves lines that match
* X does a grep and only saves lines that do not match

If the single-letter command is preceded by a number or number-range, then the edit operation only applies to that line(s). A number range may be separated by `-` hyphen or `,` comma.

##### Examples

```
12aMAX_FILE_NAME=255             insert a line AFTER line 12
12iDEFAULT_DIR = "/"             insert a line BEFORE line 12
43-45d                           delete lines 43, 44 and 45
1,20s/^#\s*/##  /                only in lines 1 through 20, replace lines that 
                                 start with a # followed by whitespace
                                 with two-# and two-spaces....to align some comments
```

The x/X patterns are wrapped in a pair of delimiter characters, typically /, although any other character is allowed (except space). Valid X commands are:

```
x/abcd/
10-20X/\w*\s*\d\d/
x!ratio x/y!
```

Similarly, the s patterns are wrapped in a triplet of delimiter characters, typcially / also. Valid 's' commands are

```
s/toronto/Toronto/
s/thier/their/
10-120s/while\s(True|False)/while 1/
s@ratio\s*=\s*num/denom@ratio = num/denom if denom else 0@
```

**Note**: you will need some free space on your disk, the same size as the source file, as a backup file is *always* made. To edit an 800k file, you should have 800k of free space.

**Note**: The functions for

* file delete (`rm, del`)
* file move (`mv, move, rename`)
* change/make/delete directory/folder (`chdir, mkdir, rmdir`)

are not included in this list, because the `os` module already has functions that implement these directly: `os.remove(), os.rename(), os.chdir(), os.mkdir(), os.rmdir()`

## Simple Command Line

By invoking `tf.main()`, you will be presented a command prompt, similar to Linux, where the prompt shows you what directory/folder you are currently in, and a '$'. 

From there, you can enter one of these commands:

```
cat   [-n] [-l<n>-<m>] <filename>
cp    <src-file> <dest-file>  
dir   [<dir name>]
grep  <pattern> <filename>
mkdir <foldername>
sed   <pattern> <filename>
mv    <src-file> <dest-file>
rm    <filename>
cd    [<dest dir>]
mkdir <dirname>
rmdir <dirname>
help
```

You can also use `copy`, `move`, `del`, `list` and `ls` as synonyms for `cp`, `mv`, `rm`, `cat` and `dir` .  The `mv` can rename directories. 

For the `cat/list` command, you can enable line numbers with `-n` and you can limit the display range with `-l n-m` where `n` and `m` are decimal numbers (and n should be less than m). These are all valid uses of `cat`

```
cat -n log.txt             # whole file
cat -n -l223 log.txt       # one line  
cat -l 223-239 log.txt     # 17 lines
cat -l244-$ log.txt        # from 244 to the end
```

For `grep`  and `sed`, the patterns are *MicroPython* regular explressions, from the `re` module. If a pattern has a space character in it, then the pattern must be wrapped in  single-quote ' characters; patterns without an embedded space char can simply be typed. [The line parser is basically a `str.split()` unless a leading ' is detected.] To include a single quote in a quoted-pattern, you can escape it with \ .

Here are some valid uses of `sed` and `grep`

```text
grep #define main.c
grep '^\s*#define\s+[A-Z]' main.c
sed 1,100s/recieve/receive/ doc.txt
sed '33-$s/it is/it\'s/' doc.txt
sed '45i   a new line of indented text' doc.txt
```    

The **REPL** typing-history is functional, so you can use the up-arrow to recall the last 4-5 commands. Use the left-arrow and backspace to correct lines that have errors.

Commands with invalid syntax return a line of information, and are ignored. Non valid commands are simply eaten and ignored.

## Limitations

In its present form, the module has these limitations:  

* filenames are limited to 255 chars
* search patterns involving \ escapes may or may not work properly
* the esp8266 implementation does not allow \1,\2 type pattern substitution
* in the simple shell
    * filenames must not have spaces
    * patterns with spaces ***must*** be quoted
    * the target of `cp`and `mv` *cannot* be a simple a directory-name as in Linux; write the whole filename *w.r.t,* the current directory
* the complexity of pattern matching is limited. 
    * try to format the grep patterns so they avoid deep stack recursion. For example, '([^#]|\\#)\*' has a very generous search term as the first half, and can cause deep-stack recursion. The equivalent '(\\#|[^#]\*)' is more likely to succeed.
* with sed-search-and-replace, the parsed line *includes* the terminal \n, so if you replace the text all the way to the end of the line, you will delete the terminal \n and this line will merge with the subsequent line
    * if the replacement is '', the line will appear to vanish, e.g. `s/^#.*//`  will delete comment lines
    * pattern matching to \n and \r does not work

## Examples

Make a simple change to a source file, perhaps modify a constant.

```
[function]  
   tf.sed('main.py','10-30s/CITY_NAME = \'Toronto\'/CITY_NAME     = \'Ottawa\'/')  
[command line]  
   sed '10-30s/CITY_NAME = \'Toronto\'/CITY_NAME = \'Ottawa\'/' main.py  
   sed 10-30s/Toronto/Ottawa/ main.py
```

Remove some comments from a source file.

```
[function]
   tf.sed('main.py','X/^#\s*TODO:/')
[command line]
   sed X/^#\s*TODO:/ main.py
```

Search a log file for an incident

```
[function]
   tf.grep('log.txt','^2021-02-12 16:\d\d',numbers=True)
[command line]
   grep [Ee]rror log.txt
   grep '2021-02-12 16:\d\d' log.txt
   [search and keep a record ]
   cp log.txt log.details
   sed 'x/2021-02-12 16:\d\d` log.details
```

## Installation

Move the 'tf.py' file over to the target. You can use `webrepl` [command line program](https://github.com/micropython/webrepl)  or the **WEBREPL** [web page](https://micropython.org/webrepl/) .

Once the module is present in the file system of the target, you can use the **REPL** command line interface to invoke it

```
 >>> import tf
tf module loaded; members cp(), cat(), cd(), _dir(), grep() and sed()
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

If you don't need the *simple command line*, you can still use the methods listed above. Feel free to cut the `tf.py` module in half by deleting everything below the line

```
    def help():
```

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
