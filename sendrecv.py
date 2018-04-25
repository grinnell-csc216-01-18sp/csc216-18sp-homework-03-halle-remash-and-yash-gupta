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

import Queue

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
        seg = Segment(msg, 'receiver')
        self.send_to_network(seg)
        self.start_timer(1)

    def receive_from_network(self, seg):
        if waitingOnACK0:
            if seg.msg == 'ACK0':
                waitingOnACK0 = False
            else:
                seg = Segment('N0', 'receiver')
                self.send_to_network(seg)
        else:
            if seg.msg == 'ACK1':
                waitingOnACK0 = True
            else:
                seg = Segment('N1', 'receiver')
                self.send_to_network(seg)

    def on_interrupt():
        if waitingOnACK0:
            seg = Segment('N0', 'receiver')
            self.send_to_network(seg)
        else:
            seg = Segment('N1', 'receiver')
            self.send_to_network(seg)


class AltReceiver(BaseReceiver):
    curAltBit0 = True

    def __init__(self):
        super(AltReceiver, self).__init__()

    def receive_from_client(self, seg):
        if curAltBit0:
            seg = Segment('ACK0', 'sender')
            self.send_to_network(seg)
            self.send_to_app(seg.msg)
            curAltBit0 = False
        else:
            seg = Segment('ACK1', 'sender')
            self.send_to_network(seg)
            self.send_to_app(seg.msg)
            curAltBit0 = True



class GBNSender(BaseSender):
    # TODO: fill me in!
    pass

class GBNReceiver(BaseReceiver):
    # TODO: fill me in!
    pass
