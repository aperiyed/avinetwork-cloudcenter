#!/usr/bin/env python
import os
import sys
import json
from cobra.mit.access import MoDirectory
from cobra.mit.session import LoginSession
from cobra.mit.request import ClassQuery
from cobra.model.fv import Tenant
from cobra.mit.request import ConfigRequest
from cobra.mit.request import DnQuery
from cobra.model.vz import RsSubjGraphAtt

import logging

logging.basicConfig(filename='apic-sg-config.log',level=logging.DEBUG)

##
# Function to be invoked when adding a service graph.
##
def add_servicegraph():
    apicURL = os.getenv("CliqrCloud_AciApicEndpoint")
    apicUser = os.getenv("CliqrCloud_AciUsername")
    apicPwd = os.getenv("CliqrCloud_AciPassword")
    apicTenant = os.getenv("CliqrCloud_AciTenantName")
    apicServiceGraphTemplate = os.getenv("Cloud_Setting_serviceGraphTemplate")

    # Handle cases where APIC URL is configured without ssl (typically, in a lab).
    if apicURL.startswith("https"):
        loginSession = LoginSession(apicURL, apicUser, apicPwd)
    else:
        loginSession = LoginSession(apicURL, apicUser, apicPwd,secure=False)

    # CliqrTier_CentOS_1_Cloud_Setting_AciPortGroup_2
    tmpString = "CliqrTier_" + os.getenv("CliqrDependencies") + "_Cloud_Setting_AciPortGroup_2"
    appProfileName = os.getenv(tmpString).split("|")[1]
    qTenant = "tn-" + apicTenant
    qString = "uni/" + qTenant + "/ap-" + appProfileName
    dnQuery = DnQuery(qString)
    dnQuery.queryTarget = 'subtree'
    dnQuery.classFilter = 'fvRsProv'
    dnQuery.subtree = 'children'
    #dnQuery.subtreePropFilter='eq(fvRsCons.tCl,"vzBrCP")'
    # Obtain Session from APIC.
    moDir = MoDirectory(loginSession)
    moDir.login()
    # Query to obtain data from Managed Object Directory.
    dmo = moDir.query(dnQuery)
    print str(dmo[0].tDn)  # Debug String. Remove from running env.
    logging.debug(" Contract String Obtained :" + dmo[0].tDn)
    # Service Graph - Query String
    qStringAbsG = "uni/" + qTenant + "/AbsGraph-" + apicServiceGraphTemplate
    graphMO = moDir.lookupByDn(qStringAbsG)
    # Subject Query String
    qStringSubj = dmo[0].tDn + "/subj-cliqr-subject"
    subjMO = moDir.lookupByDn(qStringSubj)
    # Attach Graph to Contract.
    RsSubjGraphAtt(subjMO, tnVnsAbsGraphName=graphMO.name)
    # Create Commit Object.
    nsCfg = ConfigRequest()
    nsCfg.addMo(subjMO)
    moDir.commit(nsCfg)
    contractString = dmo[0].tDn
    tmpArr = contractString.split("/")
    apicContractName = tmpArr[len(tmpArr)-1].replace("brc-","")
    aviApicContractArg = apicContractName + ":" + apicServiceGraphTemplate
    aviApicEpgName = appProfileName + ":" + os.getenv(tmpString).split("|")[2]

    params = {}
    with open('params.json', 'r') as p:
        params = json.loads(p.read())
        params['apic_contract_graph'] = aviApicContractArg
        params['apic_epg_name'] = aviApicEpgName

    logging.debug(" Dump Params :: " + json.dumps(params))   
    
    with open('params.json', 'w') as f:
        json.dump(params, f)



##
# Function to be invoked when deleting a service graph.
##
def del_servicegraph():
    apicURL = os.getenv("CliqrCloud_AciApicEndpoint")
    apicUser = os.getenv("CliqrCloud_AciUsername")
    apicPwd = os.getenv("CliqrCloud_AciPassword")



def setup_apic_servicegraph(action):
    logging.debug("Setup APIC Service Graph" )
    if action == "CREATE":
    	logging.debug(" Create Service Graph ")
        add_servicegraph()
    else:
    	logging.debug(" Delete Service Graph ")
        del_servicegraph()
