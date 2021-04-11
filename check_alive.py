#!/usr/bin/env python
#coding:utf-8

import os, sys, socket, struct, select, time
from optparse import OptionParser 

ICMP_ECHO_REQUEST = 8 
def checksum(source_string):
  sum = 0
  countTo = (len(source_string)/2)*2
  count = 0
  while count<countTo:
    thisVal = ord(source_string[count + 1])*256 + ord(source_string[count])
    sum = sum + thisVal
    sum = sum & 0xffffffff # Necessary?
    count = count + 2
  if countTo<len(source_string):
    sum = sum + ord(source_string[len(source_string) - 1])
    sum = sum & 0xffffffff # Necessary?
  sum = (sum >> 16) + (sum & 0xffff)
  sum = sum + (sum >> 16)
  answer = ~sum
  answer = answer & 0xffff
  # Swap bytes. Bugger me if I know why.
  answer = answer >> 8 | (answer << 8 & 0xff00)
  return answer
def receive_one_ping(my_socket, ID, timeout):
  """
  receive the ping from the socket.
  """
  timeLeft = timeout
  while True:
    startedSelect = time.time()
    whatReady = select.select([my_socket], [], [], timeLeft)
    howLongInSelect = (time.time() - startedSelect)
    if whatReady[0] == []: # Timeout
      return
    timeReceived = time.time()
    recPacket, addr = my_socket.recvfrom(1024)
    icmpHeader = recPacket[20:28]
    type, code, checksum, packetID, sequence = struct.unpack(
      "bbHHh", icmpHeader
    )
    if packetID == ID:
      bytesInDouble = struct.calcsize("d")
      timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
      return timeReceived - timeSent
    timeLeft = timeLeft - howLongInSelect
    if timeLeft <= 0:
      return
def send_one_ping(my_socket, dest_addr, ID):
  """
  Send one ping to the given >dest_addr<.
  """
  dest_addr = socket.gethostbyname(dest_addr)
  # Header is type (8), code (8), checksum (16), id (16), sequence (16)
  my_checksum = 0
  # Make a dummy heder with a 0 checksum.
  header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1) #压包
  #a1 = struct.unpack("bbHHh",header)  #my test
  bytesInDouble = struct.calcsize("d")
  data = (192 - bytesInDouble) * "Q"
  data = struct.pack("d", time.time()) + data
  # Calculate the checksum on the data and the dummy header.
  my_checksum = checksum(header + data)
  # Now that we have the right checksum, we put that in. It's just easier
  # to make up a new header than to stuff it into the dummy.
  header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1)
  packet = header + data
  my_socket.sendto(packet, (dest_addr, 1)) # Don't know about the 1
def do_one(dest_addr, timeout):
  icmp = socket.getprotobyname("icmp")
  try:
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
  except socket.error, (errno, msg):
    if errno == 1:
      # Operation not permitted
      msg = msg + (
        " - Note that ICMP messages can only be sent from processes"
        " running as root."
      )
      raise socket.error(msg)
    raise # raise the original error
  my_ID = os.getpid() & 0xFFFF
  send_one_ping(my_socket, dest_addr, my_ID)
  delay = receive_one_ping(my_socket, my_ID, timeout)
  my_socket.close()
  return delay
def verbose_ping(dest_addr, timeout = 2, count = 100):
  for i in xrange(count):
    print "ping %s..." % dest_addr,
    try:
      delay = do_one(dest_addr, timeout)
    except socket.gaierror, e:
      print "failed. (socket error: '%s')" % e[1]
      break
    if delay == None:
      print "failed. (timeout within %ssec.)" % timeout
    else:
      delay = delay * 1000
      print "get ping in %0.4fms" % delay
      return True
  return False

def star_convert(words):
  rnt = []
  for i in range(len(words)):
    word = words[i]
    if word == '*':
      for j in range(256):
        words_arr = list(words)
        words_arr[i] = str(j)
        new_word = "".join(words_arr)
        if "*" in new_word:
          rnt += star_convert(new_word)
        else:
          rnt.append(new_word)

  return rnt

if __name__ == '__main__':
  from optparse import OptionParser 
  parser = OptionParser() 
  parser.add_option("-p", "--ip", action="store", 
                    dest="ip", 
                    help="ipaddr,eg 10.*.*.1") 
  parser.add_option("-o", "--output", action="store", 
                    dest="output", 
                    help="save output result, eg out.txt") 

  (options, args) = parser.parse_args() 

  if not options.ip or not options.output:
    print("usage: alive.exe -h")
    sys.exit()

  for target in star_convert(options.ip):
    if verbose_ping(target,2,1):
      with open(options.output, 'a') as w:
        w.write(target + "\n")

  

  # print(verbose_ping("8.8.8.8",2,1))