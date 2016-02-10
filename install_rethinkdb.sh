#!/bin/bash

# these are the rethinkdb installation instructions from
# http://rethinkdb.com/docs/install/ubuntu/ 
source /etc/lsb-release && echo "deb http://download.rethinkdb.com/apt $DISTRIB_CODENAME main" | sudo tee /etc/apt/sources.list.d/rethinkdb.list
wget -qO- https://download.rethinkdb.com/apt/pubkey.gpg | sudo apt-key add -
sudo apt-get update
sudo apt-get -y install rethinkdb

# setup rethink to start with server, but bind ports to 0.0.0.0
sudo ln -s /vagrant/rethinkdb.conf /etc/rethinkdb/instances.d/instance1.conf 
sudo /etc/init.d/rethinkdb restart

