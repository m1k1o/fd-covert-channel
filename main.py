#!/usr/bin/python3
import os, sys, time

def send(text, fd_offset=15, bandwidth=32, pause_sec=1.5):
	# get byte array from text
	chunks = bytearray()
	chunks.extend(map(ord, text))

	# open main file
	master_fd = os.open("test_file", os.O_RDWR | os.O_CREAT)
	os.unlink("test_file")

	# init
	fds = { i:False for i in range(bandwidth) }

	# set file descriptors
	control_fd = False
	for chunk in chunks:
		# get bits from bytes
		bits = ("{0:0"+str(bandwidth)+"b}").format(chunk)

		# data fds
		new_fds = []
		for index, opened in fds.items():
			fd = fd_offset + index

			if bits[index] == "1" and not opened:
				os.dup2(master_fd, fd)
				fds[index] = True
			elif bits[index] == "0" and opened:
				os.close(fd)
				fds[index] = False

			if bits[index] == "1":
				new_fds.append(str(fd))

		# control fd
		if not control_fd:
			os.dup2(master_fd, fd_offset + bandwidth)
			control_fd = True
			new_fds.append(str(fd_offset + bandwidth))
		else:
			os.close(fd_offset + bandwidth)
			control_fd = False
		
		print("Sending " + bits + ' ' + ('[1]' if control_fd else '[0]'))
		print(", ".join(new_fds))
		time.sleep(pause_sec)

	# close control fd
	if control_fd:
		os.close(fd_offset + bandwidth)

	# close data fds
	for index, opened in fds.items():
		if opened:
			os.close(fd_offset + index)

	# close master fd
	os.close(master_fd)

def receive(proc_id, fd_offset=15, bandwidth=32, pause_sec=1.5, max_skipped=10):
	state = True
	skipped = None
	chunks = []
	while True:
		try:
			files = os.listdir('/proc/{}/fd'.format(proc_id))
		except Exception as e:
			if skipped is None:
				raise e
			
			# finished
			break

		# init
		chunk = [str(0) for i in range(bandwidth)]
		fds = []
		control_fd = False

		for name in files:
			fd = int(name) - fd_offset

			if fd == bandwidth:
				control_fd = True

			if fd < 0 or fd >= bandwidth:
				continue

			chunk[fd] = str(1)
			fds.append(name)

		# if none has been skipped, its just waiting for sender to send data
		if control_fd == 0 and skipped is None:
			print("Waiting...")
			time.sleep(pause_sec)
			continue

		byte_str = "".join(chunk)
		if state != control_fd:
			print("Skipping " + byte_str + (' [1]' if control_fd else ' [0]'))
			skipped += 1

			if skipped > max_skipped:
				raise Exception("Maximum skipped exceeded...")
				break

			time.sleep(pause_sec)
			continue

		print("Received " + byte_str + (' [1]' if control_fd else ' [0]'))
		print(", ".join(fds))

		# get chunk
		chunk = int(byte_str, 2)
		chunks.append(chunk)

		state = not state
		skipped = 0
		time.sleep(pause_sec)
		
	text = ''
	for chunk in chunks:
		text += chr(chunk)

	return text

#
# CONSOLE
#

import argparse
import sys

def send_args(args):
	# get PID
	pid = os.getpid()
	print("Listen on PID: {}".format(pid))

	# get text
	with open(args.input, 'r', encoding='utf-8') as file:
		text = file.read()

	input("Press Enter to start broadcast...")

	send(
		text=text,
		fd_offset=args.fd_offset,
		bandwidth=args.bandwidth,
		pause_sec=args.pause
	)

	print("Sent.")

def receive_args(args):
	text = receive(
		proc_id=args.proc_id,
		fd_offset=args.fd_offset,
		bandwidth=args.bandwidth,
		pause_sec=args.pause,
		max_skipped=args.timeout
	)

	with open(args.output, 'w', encoding='utf-8') as file:
		file.write(text)

	print("Received.")


# send the top-level parser
parser = argparse.ArgumentParser(
	prog='fd-covert-channel',
	description='Send text files using covert channel in file descriptors of process'
)
parser.add_argument('-f', '--fd-offset', type=int, help='file descriptor offset', required=False, default=15)
parser.add_argument('-b', '--bandwidth', type=int, help='bandwidth', required=False, default=32)
parser.add_argument('-p', '--pause', type=int, help='pause between broadcasts in seconds', required=False, default=0.5)
subparsers = parser.add_subparsers()

# send the parser for the "send" command
parser_send = subparsers.add_parser('send', help='send data')
parser_send.add_argument('input', type=str, help='input file')
parser_send.set_defaults(func=send_args) 

# send the parser for the "receive" command
parser_receive = subparsers.add_parser('receive', help='receive file from sender')
parser_receive.add_argument('proc_id', type=str, help='proc id of sender')
parser_receive.add_argument('-t', '--timeout', type=int, help='maximum skipped transmissions after it fails', default=10, required=False)
parser_receive.add_argument('-o', '--output', type=str, help='output file', default="out.txt", required=False)
parser_receive.set_defaults(func=receive_args)

# parse argument lists
args = parser.parse_args()

# run function
try:
	args.func(args)
	sys.exit(0)
except AttributeError:
	parser.print_help()
	parser.exit()
except Exception as e:
	print(e)
	sys.exit(1)
