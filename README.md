Salt Event IRC Bot
==

Motivation: Keep track of commands and their result in realtime on IRC.


Example output
--


    11:26 <salt>    [20140703022531605667] state.sls nginx,php5-fpm meneldur root
    11:26 <salt>    [20140703022531605667] state.sls nginx,php5-fpm meneldur SUCCESS! OK:158 Failed:56

    13:26 <salt>    [20140703022655875638] test.version amandil,elendil root
    13:26 <salt>    [20140703022655875638] test.version elendil SUCCESS! 2014.1.4
    13:26 <salt>    [20140703022655875638] test.version amandil SUCCESS! 2014.1.4


Configure
--

Copy config.yaml.example to config.yaml and edit the file to fit your needs.

    cp config.yaml.example config.yaml
    $EDITOR config.yaml


Dependencies
--


Install dependencies.

    sudo apt-get install python-twisted-words

Launch
--

Use twistd with your own arguments to fit your needs. The simplest variant is:


    twistd -y saltbot.py

