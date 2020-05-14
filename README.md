# fd-covert-channel
Transmit text files using covert channel in file descriptors of proccess.

```
$ ./main.py -h
usage: fd-covert-channel [-h] [-f FD_OFFSET] [-b BANDWIDTH] [-p PAUSE]
                         {send,receive} ...

Send text files using covert channel in file descriptors of proccess

positional arguments:
  {send,receive}
    send                send data
    receive             receive file from sender

optional arguments:
  -h, --help            show this help message and exit
  -f FD_OFFSET, --fd-offset FD_OFFSET
                        file descriptor offset
  -b BANDWIDTH, --bandwidth BANDWIDTH
                        bandwidth
  -p PAUSE, --pause PAUSE
                        pause between broadcasts in seconds
```
