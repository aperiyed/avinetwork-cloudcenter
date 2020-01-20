#!/usr/bin/env python
import os
from subprocess import STDOUT, check_call
import pip
import sys
import logging

logging.basicConfig(filename='apic_invocation.log',level=logging.DEBUG)

if __name__ == '__main__':
    try:
        print 'apic sg install'
        logging.debug("Starting APIC SG Setup")
        from apic_sginstall import setup_apic_servicegraph
        action = 'CREATE' if len(sys.argv) < 2 else sys.argv[1].upper()
        logging.debug(" Executing APIC SG Action")
        setup_apic_servicegraph(action)
    except Exception as e:
        print e
        f = open('FAILURE','w')
        f.write(str(e))
        f.close()

