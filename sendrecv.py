##
# CSC 216 (Spring 2018)
# Reliable Transport Protocols (Homework 3)
#
# Sender-receiver code for the RDP simulation program.  You should provide
# your implementation for the homework in this file.
#
# Your various Sender implementations should inherit from the BaseSender
# class which exposes the following important methods you should use in your
# implementations:
#
# - sender.send_to_network(seg): sends the given segment to network to be
#   delivered to the appropriate recipient.
# - sender.start_timer(interval): starts a timer that will fire once interval
#   steps have passed in the simulation.  When the timer expires, the sender's
#   on_interrupt() method is called (which should be overridden in subclasses
#   if timer functionality is desired)
#
# Your various Receiver implementations should also inherit from the
# BaseReceiver class which exposes the following important methods you should
# use in your implementations:
#
# - sender.send_to_network(seg): sends the given segment to network to be
#   delivered to the appropriate recipient.
# - sender.send_to_app(msg): sends the given message to receiver's application
#   layer (such a message has successfully traveled from sender to receiver)
#
# Subclasses of both BaseSender and BaseReceiver must implement various methods.
# See the NaiveSender and NaiveReceiver implementations below for more details.
##

from sendrecvbase import BaseSender, BaseReceiver
from copy import deepcopy
import Queue

def firstInQueue(q):
	return q.queue[0]

class Segment:
    def __init__(self, msg, dst, alt):
        self.msg = msg
        self.dst = dst
        self.alt = alt

class NaiveSender(BaseSender):
    def __init__(self, app_interval):
        super(NaiveSender, self).__init__(app_interval)

    def receive_from_app(self, msg):
        seg = Segment(msg, 'receiver', 0)
        self.send_to_network(seg)

    def receive_from_network(self, seg):
        pass    # Nothing to do!

    def on_interrupt():
        pass    # Nothing to do!

class NaiveReceiver(BaseReceiver):
    def __init__(self):
        super(NaiveReceiver, self).__init__()

    def receive_from_client(self, seg):
        self.send_to_app(seg.msg)

class AltSender(BaseSender):
    waitingOnACK0 = True

    def __init__(self, app_interval):
        super(AltSender, self).__init__(app_interval)

    def receive_from_app(self, msg):
        bit = 0 if self.waitingOnACK0 else 1
        seg = Segment(msg, 'receiver', bit)
        self.send_to_network(seg)
        self.start_timer(16)

    def receive_from_network(self, seg):
        bit = 0 if self.waitingOnACK0 else 1
        if self.waitingOnACK0:
            if seg.msg == 'ACK0':
                self.waitingOnACK0 = False
            else:
                seg = Segment('NAK0', 'receiver', bit)
                self.send_to_network(seg)
        else:
            if seg.msg == 'ACK1':
                self.waitingOnACK0 = True
            else:
                seg = Segment('NAK1', 'receiver', bit)
                self.send_to_network(seg)

    def on_interrupt(self):
        BaseSender.end_timer(self)
        bit = 0 if self.waitingOnACK0 else 1
        if self.waitingOnACK0:
            seg = Segment('NAK0', 'receiver', bit)
            self.send_to_network(seg)
        else:
            seg = Segment('NAK1', 'receiver', bit)
            self.send_to_network(seg)


class AltReceiver(BaseReceiver):
    curAltBit0 = True

    def __init__(self):
        super(AltReceiver, self).__init__()

    def receive_from_client(self, seg):
        bit = 0 if self.curAltBit0 else 1
        if self.curAltBit0:
            ack = Segment('ACK0', 'sender', bit)
            self.send_to_network(ack)
            self.send_to_app(seg.msg)
            self.curAltBit0 = False
        else:
            ack = Segment('ACK1', 'sender', bit)
            self.send_to_network(ack)
            self.send_to_app(seg.msg)
            self.curAltBit0 = True

class GBNSender(BaseSender):
	def __init__(self, app_interval):
		super(GBNSender, self).__init__(app_interval)
		self.oldestSeq = 1
		self.nextSeq = 2
		self.maxSeq = 3
		self.queue = Queue.Queue()

	def receive_from_app(self, msg):
		seg = Segment(msg, 'receiver', self.nextSeq)
		self.queue.put(seg)
		self.send_to_network(deepcopy(seg))
		self.nextSeq += 1
		if self.queue.qsize() == self.maxSeq:
			self.disallow_app_msgs()
		if self.queue.qsize() == 1:
			self.start_timer(15)

	def receive_from_network(self, seg):
		if seg.msg == 'ACK' and seg.alt > self.oldestSeq:
			self.oldestSeq = seg.alt
			while not self.queue.empty() and firstInQueue(self.queue).alt < self.oldestSeq:
				self.queue.get()
			self.allow_app_msgs()

	def on_interrupt(self):
		for seg in list(self.queue.queue):
			self.send_to_network(deepcopy(seg))
		self.start_timer(15)

class GBNReceiver(BaseReceiver):
	def __init__(self):
		super(GBNReceiver, self).__init__()
		self.recvSeq = 1

	def receive_from_client(self, seg):
		if seg.msg != '<CORRUPTED>' and seg.alt == self.recvSeq + 1:
			self.recvSeq += 1
			self.send_to_app(seg.msg)
			seg2 = Segment('ACK', 'sender', self.recvSeq)
		else:
			seg2 = Segment('ACK', 'sender', self.recvSeq)
		self.send_to_network(seg2)
