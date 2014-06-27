Salt Event IRC Bot
==

Motivation: Keep track of commands and their result in realtime on IRC.



Configure
--

Copy config.yaml.example to config.yaml and edit the file to fit your needs.


Dependencies
--


Install dependencies.

    sudo apt-get install python-twisted-words

Launch
--

Use twistd with your own arguments to fit your needs. The simplest variant is:


    twistd -y saltbot.py
