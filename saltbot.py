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
from yaml import safe_load
import threading

import thread, os, time, sys, string

config = safe_load(file('config.yaml').read())

GreenColor = '\x033,1'
YellowColor = '\x038,1'
RedColor = '\x034,1'

def salteventlistener(bot, run):
    import isea
    import iseafilter
    import iseaformatter
    # Reload code on every thread start
    reload(isea)
    reload(iseafilter)
    reload(iseaformatter)
    from isea import Isea
    from iseafilter import IseaFilter
    from iseaformatter import IseaFormatter
    def output(data):
        bot.msg(config['irc']['channel'], IseaFormatter(data), length=400)

    isea = Isea()
    # TODO:
    # support more elaborate filtering
    f2 = IseaFilter('Fun')
    f2.add_filter('fun', config['filters']['functions'])
    isea.add_filter(f2)
    #bot.msg(config['irc']['channel'], 'Isea object: {}'.format(isea))
    isea.listen(config['salt']['target'], '/var/run/salt', output, run)

class ircProtocol(irc.IRCClient):
    """A logging IRC bot."""

    nickname = config['irc']['nick']
    password = config['irc']['password']
    
    def __init__(self):
        self.start()

    def start(self):
        from isea import IseaController
        self.run = IseaController(True)
        self.isea_thread = threading.Thread(target=salteventlistener, args=(self,self.run,))
        self.isea_thread.start()

    def stop(self):
        self.run.set(False)

    def running(self):
        return self.isea_thread.isAlive()

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
        self.join(config['irc']['channel'])
        self.factory.client = self
        # Start reactor
        
        if not self.running():
            self.start()

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        #self.thread = thread.start_new_thread(recupere_pipe, (self,))
        #d = threads.deferToThread(self.doLongCalculation)
        #d.addCallback(self.printResult)
        self.msg(channel, 'Be greeted. I return from the dead.')
        #bot = self
        #self.salteventthread = thread.start_new_thread(salteventlistener, (self,))
        #reactor.callFromThread(salteventlistener, self)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        log.msg("<%s> %s" % (user, msg))

        if msg == '!stop':
            if not self.running():
                return

            self.stop()
            while self.running():
                ''' Waiting for event listen loop to to terminate'''
                pass
            self.msg(channel, 'Stopped ISEA!')
            return
        elif msg == '!start':
            if self.running():
                self.msg(channel, 'ISEA is already running!')
                return
            else:
                self.start()
                self.msg(config['irc']['channel'], 'Started ISEA!')
            return
        elif msg == '!reload':
            self.msg(channel, 'Reloading ISEA!')
            self.stop()
            
            while self.running():
                pass

            self.start()
            self.msg(channel, 'Reloaded ISEA!')
            return

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
