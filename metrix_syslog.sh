#!/bin/bash

rm -f '/home/ilkka/metrix_syslog.txt'
grep 'metrix\|telegram' /var/log/syslog >> /home/ilkka/metrix_syslog.txt
date >> /home/ilkka/metrix_syslog.txt
