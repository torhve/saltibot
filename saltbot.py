#!/usr/bin/env python
# This script is under GPL License v2
# (c) Jean-Michel LACROIX 2006 (jm-lacroix@savigny.org)
# (c) Tor Hveem 2008-2014

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, threads
from twisted.python import log
from twisted.internet import threads
from twisted.internet.protocol import Protocol
from twisted.application import internet, service
from Isea import Isea
from IseaFilter import IseaFilter
from IseaFormatter import IseaFormatter
from yaml import safe_load

import thread, os, time, sys

config = safe_load(file('config.yaml').read())

GreenColor = '\x033,1'
YellowColor = '\x038,1'
RedColor = '\x034,1'
ircoutput = None

# system imports
def salteventlistener(bot):
    def output(data):
        bot.msg(config['irc']['channel'], IseaFormatter(data), length=400)

    isea = Isea()
    f2 = IseaFilter('Fun')
    f2.add_filter('fun', ['state.sls','test.ping', 'test.version', 'state.highstate'])
    isea.add_filter(f2)
    isea.listen('master', '/var/run/salt', output)

class ircProtocol(irc.IRCClient):
    """A logging IRC bot."""

    nickname = config['irc']['nick']
    password = config['irc']['password']

    def printResult(self, result):
        self.msg(config['irc']['channel'], result)
        d = threads.deferToThread(self.doLongCalculation)
        d.addCallback(self.printResult)

    #def connectionMade(self):
    #    self.factory.client = self
    #    irc.IRCClient.connectionMade(self)
    #   irc.IRCClient.connectionMade(self)


    #def connectionLost(self, reason):
    #    irc.IRCClient.connectionLost(self, reason)
    #    try:
    #        self.thread.exit()
    #    except Exception, e:
    #        print e
    #        pass

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        ircoutput = self.msg
        self.join(config['irc']['channel'])
        self.factory.client = self

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        #self.thread = thread.start_new_thread(recupere_pipe, (self,))
        #d = threads.deferToThread(self.doLongCalculation)
        #d.addCallback(self.printResult)
        self.msg(channel, 'Be greeted. I return from the dead.')
        #bot = self
        #self.salteventthread = thread.start_new_thread(salteventlistener, (self,))
        reactor.callInThread(salteventlistener, self)
        #reactor.callFromThread(salteventlistener, self)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        #self.logger.log("<%s> %s" % (user, msg))

        # Check to see if they're sending me a private message
        if channel == self.nickname:
            msg = "It isn't nice to whisper!  Play nice with the group."
            self.msg(user, msg)
            return

        # Otherwise check to see if it is a message directed at me
        if msg.startswith(self.nickname + ":"):
            msg = "%s: I am a bot. Why so serious?" % user
            self.msg(channel, msg)
            #self.logger.log("<%s> %s" % (self.nickname, msg))

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        #self.logger.log("* %s %s" % (user, msg))

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        #self.logger.log("%s is now known as %s" % (old_nick, new_nick))

    def alert(self, msg):
        self.IRCClient.msg(config['irc']['channel'], msg)

class LogBotFactory(protocol.ClientFactory):
    """A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """

    # the class of the protocol to build when new connection is made
    protocol = ircProtocol

    #def __init__(self), channel):
    #    self.channel = channel
#
    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


application = service.Application("saltbot")

ircf = LogBotFactory()
irc = internet.TCPClient(config['irc']['server'], config['irc']['port'], ircf)
irc.setName('irc')
irc.setServiceParent(application)
