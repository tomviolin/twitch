#!/bin/bash
cd /home/tomh/twitch

if ( pgrep -f '[t]eststream' > /dev/null ); then 
	test
else
	/usr/bin/screen -d -m /home/tomh/twitch/teststream.py
fi
