**DISCLAIMER**: THIS SOFTWARE IS HIGHLY EXPERIMENTAL, ONLY DEMOSTRATIONAL PROOF OF CONCEPT AND SHOULD NOT BE USED TO SEND ANY DATA RELIABLY.

# fd-covert-channel
Transmit text files using covert channel in file descriptors of process.

Every process can open a file. Those file descriptors can everyone in the system see. This covert channel consists of permutating file descriptors of process, where `1` means file is opened and `0` file is closed. Receiver can read this time changing sequence and recover file.

- **FD_OFFSET** - file descriptor offset is offet in created file descriptors.
- **BANDWIDTH** - desired bandwidth for sent data. Control channel is outside of selected bandwidth. It can tell receiver whether any change in transmission occured.
- **PAUSE** - after one broadcast, how long will program wait until another broadcast.

```
$ ./main.py -h
usage: fd-covert-channel [-h] [-f FD_OFFSET] [-b BANDWIDTH] [-p PAUSE]
                         {send,receive} ...

Send text files using covert channel in file descriptors of process

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

**Please note** that this program can only send text files. It will read whole text file into memory, so please take that into consideration.

## Demo

Sender
```sh
$ echo 'Test 123' > test
$ ./main.py send test
Listen on PID: 18514
Press Enter to start broadcast...
Sending 00000000000000000000000001010100 [1]
40, 42, 44, 47
Sending 00000000000000000000000001100101 [0]
40, 41, 44, 46
Sending 00000000000000000000000001110011 [1]
40, 41, 42, 45, 46, 47
Sending 00000000000000000000000001110100 [0]
40, 41, 42, 44
Sending 00000000000000000000000000100000 [1]
41, 47
Sending 00000000000000000000000000110001 [0]
41, 42, 46
Sending 00000000000000000000000000110010 [1]
41, 42, 45, 47
Sending 00000000000000000000000000110011 [0]
41, 42, 45, 46
Sending 00000000000000000000000000001010 [1]
43, 45, 47
Sent.
```

Receiver:
```sh
$ ./main.py receive 18514
Waiting...
Waiting...
Waiting...
Waiting...
Received 00000000000000000000000001010100 [1]
40, 42, 44
Received 00000000000000000000000001100101 [0]
40, 41, 44, 46
Received 00000000000000000000000001110011 [1]
40, 41, 42, 45, 46
Received 00000000000000000000000001110100 [0]
40, 41, 42, 44
Received 00000000000000000000000000100000 [1]
41
Received 00000000000000000000000000110001 [0]
41, 42, 46
Received 00000000000000000000000000110010 [1]
41, 42, 45
Received 00000000000000000000000000110011 [0]
41, 42, 45, 46
Received 00000000000000000000000000001010 [1]
43, 45
Received.
$ cat out.txt
Test 123
```

## Requirements
- python 3
- unix operating system
