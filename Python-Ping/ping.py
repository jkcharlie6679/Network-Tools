#!/usr/bin/env python3

import socket
import os
import time
import sys
import struct
import select
import argparse
from datetime import datetime

if sys.platform.startswith('win32'):
	timer = time.perf_counter
else:
	timer = time.time

ICMP_ECHO = 8
ICMP_ECHOREPLY = 0
CODE = 0
MIN_SLEEP = 1000.00

def calculate_checksum(packet):

	countTo = (len(packet) // 2) * 2

	count = 0
	sum = 0

	while count < countTo:
		if sys.byteorder == "little":
			loByte = packet[count]
			hiByte = packet[count + 1]
		else:
			loByte = packet[count + 1]
			hiByte = packet[count]
		sum = sum + (hiByte * 256 + loByte)
		count += 2

	if countTo < len(packet):
		sum += packet[count]

	# sum &= 0xffffffff
	
	sum = (sum >> 16) + (sum & 0xffff)  # adding the higher order 16 bits and lower order 16 bits
	sum += (sum >> 16)

	answer = ~sum & 0xffff
	answer = answer >> 8 | (answer << 8 & 0xff00)
	# answer = socket.htons(answer)

	return answer


def is_valid_ip(hostname_ip):
	
	ip_parts = hostname_ip.strip().split('.')

	if len(ip_parts) != 4:
		return False
	
	for part in ip_parts:

		try:
			if int(part) < 0 or int(part) > 255:
				return False

		except ValueError:
			return False

	return True


def to_ip(hostname):
	if is_valid_ip(hostname):
		return hostname
	return socket.gethostbyname(hostname)


class Ping:

	def __init__(self, destination_server, count_of_packets, timeout_in_ms, packet_size, showtime):
		self.destination_server = destination_server
		self.count_of_packets = count_of_packets
		self.timeout_in_ms = timeout_in_ms
		self.packet_size = packet_size
		self.showtime = showtime
		if self.packet_size > 65507:
			print("ping: packet size too large: {} > 65507".format(self.packet_size))
			sys.exit()
		self.identifier = os.getpid() & 0xffff
		self.seq_no = -1
		try:
			self.destination_ip = to_ip(self.destination_server)
		except socket.gaierror as e:
			self.print_unknown_host()
			sys.exit()

		self.sent_packets = 0
		self.received_packets = 0
		self.min_delay = 999999999.0
		self.max_delay = 0.0
		self.total_delay = 0.0

	def print_start(self):
		print(
			"PYTHON-PING {} ({}): {} data bytes".format(self.destination_server, self.destination_ip, self.packet_size))

	def print_unknown_host(self):
		print("python-ping: cannot resolve {}: Unknown host".format(self.destination_server))

	def print_timeout(self):
		print("Request timeout for icmp_seq {}".format(self.seq_no))

	def print_success(self, data_len, from_address, ttl, delay):
		if self.showtime == False:
			print("{} bytes from {}: icmp_seq={} ttl={} time={:.3f} ms".format(data_len, from_address, self.seq_no, ttl, delay))
		else:
			print("{} {} bytes from {}: icmp_seq={} ttl={} time={:.3f} ms".format(datetime.now().time(), data_len, from_address, self.seq_no, ttl, delay))


	def print_exit(self):
		print("--- {} ping statistics ---".format(self.destination_server))

		if self.sent_packets != 0:
			packet_loss = ((self.sent_packets - self.received_packets) * 100) / self.sent_packets
			print("{} packets transmitted, {} packets received, {:.1f}% packet loss".format(self.sent_packets, self.
																					   received_packets, packet_loss))

			avg = self.total_delay/self.sent_packets
			if self.received_packets > 0:
				print("round-trip min/avg/max = {:.3f}/{:.3f}/{:.3f} ms".format(self.min_delay, avg, self.max_delay))

		else:
			print("{} packets transmitted, {} packets received".format(self.sent_packets, self.received_packets))

	@staticmethod
	def header_to_dict(keys, header, struct_format):
		values = struct.unpack(struct_format, header)
		return dict(zip(keys, values))

	def start_ping(self):

		try:
			if self.count_of_packets > 0:
				while self.count_of_packets > 0:
					self.pinger()
					self.count_of_packets -= 1
			else:
				while True:
					self.pinger()
					self.count_of_packets -= 1

		except KeyboardInterrupt:  # handle Ctrl+C
			print()

		self.print_exit()

	def pinger(self):

		try:
			icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("ICMP"))
		except socket.error as err:
			if err.errno == 1:
				print("Operation not permitted: ICMP messages can only be sent from a process running as root")
			else:
				print("Error: {}".format(err))

			sys.exit()

		if self.seq_no == -1:
			self.print_start()

		self.seq_no += 1
		time_values = self.send_icmp_request(icmp_socket)

		if time_values is None:
			time.sleep(MIN_SLEEP / 1000.00)
			return

		send_time, start_of_wait = map(float, time_values)
		self.sent_packets += 1

		receive_time, ttl, data_len, from_address = self.receive_icmp_reply(icmp_socket)
		icmp_socket.close()

		if receive_time:
			self.received_packets += 1
			delay = (receive_time - send_time) * 1000.00
			if self.min_delay > delay:
				self.min_delay = delay

			if self.max_delay < delay:
				self.max_delay = delay

			self.total_delay += delay

			self.print_success(data_len, from_address, ttl, delay)

			if MIN_SLEEP > delay:
				time.sleep((MIN_SLEEP - delay) / 1000.00)

	def send_icmp_request(self, icmp_socket):

		checksum = 0
		startvalue = 65
		header = struct.pack("!BBHHH", ICMP_ECHO, CODE, checksum, self.identifier, self.seq_no)
		# Type(1) Code(1) checksum(2) identifier(2) seq_no(2)

		payload = []
		for i in range(startvalue, startvalue + self.packet_size):
			payload.append(i & 0xff)
		
		data = bytes(payload)
		
		checksum = calculate_checksum(header + data)
		
		header = struct.pack("!BBHHH", ICMP_ECHO, CODE, checksum, self.identifier, self.seq_no)
		
		packet = header + data

		send_time = timer()

		try:
			icmp_socket.sendto(packet, (self.destination_server, 1))
			start_of_wait = timer()
		except socket.error as err:
			print("General error: %s", err)
			icmp_socket.close()
			return

		return send_time, start_of_wait

	def receive_icmp_reply(self, icmp_socket):

		timeout = self.timeout_in_ms / 1000  # converting timeout to s

		while True:

			inputready, _, _ = select.select([icmp_socket], [], [], timeout)
			receive_time = timer()

			if not inputready:  # timeout
				self.print_timeout()
				return None, 0, 0, 0

			packet_data, address = icmp_socket.recvfrom(2048)
			# packet_data = IP_header + icmp_header
			# icmp_header = type(1) code(1) checksum(2) identifier(2) seq_num(2)
			icmp_keys = ['type', 'code', 'checksum', 'identifier', 'sequence number']
			icmp_header = self.header_to_dict(icmp_keys, packet_data[20:28], "!BBHHH")

			if icmp_header['identifier'] == self.identifier and icmp_header['sequence number'] == self.seq_no:

				ip_keys = ['VersionIHL', 'Type_of_Service', 'Total_Length', 'Identification', 'Flags_FragOffset', 'TTL', 'Protocol',
						   'Header_Checksum', 'Source_IP', 'Destination_IP']
				ip_header = self.header_to_dict(ip_keys, packet_data[:20], "!BBHHHBBHII")
				data_len = len(packet_data) - 28
				return receive_time, ip_header['TTL'], data_len, address[0]


def create_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument('destination_server')
	parser.add_argument('-c', dest='count', required=False, nargs='?', default=-1, type=int, help='Count of packets', metavar='4')
	parser.add_argument('-t', dest='timeout', required=False, nargs='?', default=1000, type=int, help='Timeout in ms', metavar='1000')
	parser.add_argument('-p', dest='packet_size', required=False, nargs='?', default=64, type=int, help='Packet size in bytes', metavar='64')
	parser.add_argument('-i', dest='wait', required=False, nargs='?', default=1, type=float, help='Wait time in s', metavar='1')
	parser.add_argument('--show-time', dest='showtime', action="store_true", help='Show system time')
	return parser


def ping(destination_server, timeout=1000, count=-1, packet_size=64, showtime=False):
	p = Ping(destination_server, count, timeout, packet_size, showtime)
	p.start_ping()


if __name__ == '__main__':
	parser = create_parser()
	args = parser.parse_args(sys.argv[1:])
	destination_server = args.destination_server
	timeout = args.timeout
	packet_size = args.packet_size
	count = args.count
	MIN_SLEEP = MIN_SLEEP * args.wait
	showtime = args.showtime
	ping(destination_server, timeout, count, packet_size, showtime)
