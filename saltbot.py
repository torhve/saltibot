#!/usr/bin/env python
# This script is under GPL License v2
# (c) Jean-Michel LACROIX 2006 (jm-lacroix@savigny.org)
# (c) Tor Hveem 2008-2014

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, threads
from twisted.python import log, rebuild
from twisted.python.filepath import FilePath
from twisted.internet import threads
from twisted.internet.protocol import Protocol
from twisted.application import internet, service
import isea
import iseafilter
import iseaformatter
from isea import Isea
from isea import IseaController
from iseafilter import IseaFilter
from iseaformatter import IseaFormatter
from yaml import safe_load
import threading

import thread, os, time, sys, string

config = safe_load(file('config.yaml').read())

GreenColor = '\x033,1'
YellowColor = '\x038,1'
RedColor = '\x034,1'
ircoutput = None

def clearcache():
    isea_files = ['isea.py', 'iseaformatter.py', 'iseafilter.py']

    for f in isea_files:
        fp = FilePath(f)
        bc = fp.sibling(string.join([string.split(f, '.')[0], '.pyc'], ''))
        if bc.exists():
            bc.remove()

def salteventlistener(bot, run):
    def output(data):
        bot.msg(config['irc']['channel'], IseaFormatter(data), length=400)

    isea = Isea()
    # TODO:
    # support more elaborate filtering
    f2 = IseaFilter('Fun')
    f2.add_filter('fun', config['filters']['functions'])
    isea.add_filter(f2)
    bot.msg(config['irc']['channel'], 'Isea object: {}'.format(isea))
    isea.listen('master', '/var/run/salt', output, run)

class ircProtocol(irc.IRCClient):
    """A logging IRC bot."""

    nickname = config['irc']['nick']
    password = config['irc']['password']
    
    def __init__(self):
        self.run = IseaController(True)
        self.isea_thread = threading.Thread(target=salteventlistener, args=(self,self.run,))

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
        # Start reactor
        
        if not self.isea_thread.isAlive():
            print('Starting ISEA thread')
            self.isea_thread.start()
            print('Started ISEA thread')

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
        #self.logger.log("<%s> %s" % (user, msg))

        if '!stop' in msg:
            if not self.run.get():
                self.msg(channel, 'ISEA is not running!')
                return

            self.msg(channel, 'Stopping ISEA!')
            self.run.set(False)
            
            while self.isea_thread.isAlive():
                pass
        
            self.msg(channel, 'Stopped ISEA!')
            return

        if '!start' in msg:
            if self.run.get():
                self.msg(channel, 'ISEA is already running!')
                return

            self.msg(channel, 'Starting ISEA!')
            self.run.set(True)
            self.isea_thread = threading.Thread(target=salteventlistener, args=(self,self.run,))
            self.isea_thread.start()
            self.msg(channel, 'Started ISEA!')
            return

        if '!reload' in msg:
            self.msg(channel, 'Reloading ISEA!')
            self.run.set(False)
            
            while self.isea_thread.isAlive():
                pass

            clearcache()

            rebuild.rebuild(isea)
            rebuild.rebuild(iseafilter)
            rebuild.rebuild(iseaformatter)

            self.run.set(True)
            self.isea_thread = threading.Thread(target=salteventlistener, args=(self,self.run,))
            self.isea_thread.start()
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
