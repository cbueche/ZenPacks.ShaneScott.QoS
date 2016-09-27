#!/usr/bin/env python
#
# a QoS discovery tool
#
# Ch. Bueche <bueche@netnea.com>
#
# 4.8.2011    : CB    : initial version to decode the QoS configuration of a device
# 1.11.2013   : CB    : support non-standard indexing of cbQosObjectsTable in Cisco ASR
# 15.9.2016   : CB    : support for Zenoss 4.x and use getbulk instead of getnext
#
# Usage : ./qos_parser.py -c community -d device [-D]
#


import sys
import logging
import pprint
from pysnmp.hlapi import *
from pysnmp import __version__ as pysnmp_version
from optparse import OptionParser


# a function to run a snmpbulkget on an OID, and get a dictionary back
# ---------------------------------------------------------------------------------------
def get_table(hostname, port, community, oid):
# ---------------------------------------------------------------------------------------

    # some tuning that might need adjustements
    nonRepeaters = 0
    maxRepetitions = 20

    logger.debug('get_table : hostname=%s, port=%s, community=%s, oid=%s', hostname, port, 'community', oid)
    table = {}
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in bulkCmd(SnmpEngine(),
                              CommunityData(community, mpModel=1),
                              UdpTransportTarget((hostname, port)),
                              ContextData(),
                              nonRepeaters,
                              maxRepetitions,
                              ObjectType(ObjectIdentity(oid)),
                              lexicographicMode=False,
                              lookupMib=False):

        if errorIndication:
            logger.critical('error : %s', errorIndication)
            print "FATAL 1, exit"
            sys.exit(1)
        else:
            if errorStatus:
                logger.critical('%s at %s\n' % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[-1][int(errorIndex)-1] or '?'
                    ))
                sys.exit(1)
                print "FATAL 2, exit"
            else:
                # sucessful walk. Store the index and values in a dictionary
                for varBind in varBinds:
                    table[varBind[0].prettyPrint()] = varBind[1].prettyPrint()

    logger.debug('get_table : done')

    return table

# end def get_table
# ---------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------
def get_cbQosServicePolicyTable(cbQosServicePolicyEntries):
# ---------------------------------------------------------------------------------------

    logger.debug("in get_cbQosServicePolicyTable")
    # store the stuff in a pre-cooked dictionary
    cbQosServicePolicyTable = AutoVivification()

    for cbQosServicePolicyEntry in cbQosServicePolicyEntries.keys():
        array = cbQosServicePolicyEntry.split('.')
        pName = array[13]
        cbQosPolicyIndex = array[14]

        if pName == '2':
            pVal = 'cbQosIfType'
        elif pName == '3':
            pVal = 'cbQosPolicyDirection'
        elif pName == '4':
            pVal = 'cbQosIfIndex'
        elif pName == '5':
            pVal = 'cbQosFrDLCI'
        elif pName == '6':
            pVal = 'cbQosAtmVPI'
        elif pName == '7':
            pVal = 'cbQosAtmVCI'
        elif pName == '8':
            pVal = 'cbQosEntityIndex'
        elif pName == '9':
            pVal = 'cbQosVlanIndex'
        else:
            pVal = pName

        cbQosServicePolicyTable[cbQosPolicyIndex][pVal] = cbQosServicePolicyEntries[cbQosServicePolicyEntry]

    return cbQosServicePolicyTable

# end def get_cbQosServicePolicyTable(cbQosServicePolicyEntries):
# ---------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------
def get_ifEntriesTable(ifEntries):
# ---------------------------------------------------------------------------------------

    logger.debug("in get_ifEntriesTable")
    # store the stuff in a pre-cooked dictionary

    ifEntriesTable = {}
    for ifEntry in ifEntries.keys():
        array = ifEntry.split('.')
        ifEntryIndex = array[10]

        ifEntriesTable[ifEntryIndex] = ifEntries[ifEntry]

    return ifEntriesTable

# end def get_ifEntriesTable
# ---------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------
def get_cbQosObjectTable(cbQosObjectsEntries):
# ---------------------------------------------------------------------------------------

    logger.debug("in get_cbQosObjectTable")
    # store the stuff in a pre-cooked dictionary
    cbQosObjectTable = AutoVivification()

    for cbQosObjectsEntry in cbQosObjectsEntries.keys():
        array = cbQosObjectsEntry.split('.')
        pName = array[13];
        cbQosPolicyIndex = array[14];
        cbQosObjectsIndex = array[15];

        if pName == '2':
            pVal = 'cbQosConfigIndex'
        elif pName == '3':
            pVal = 'cbQosObjectsType'
        elif pName == '4':
            pVal = 'cbQosParentObjectsIndex'
        else:
            pVal = pName

        cbQosObjectTable[cbQosPolicyIndex]["QosObjectsEntry"][cbQosObjectsIndex][pVal] = cbQosObjectsEntries[cbQosObjectsEntry]

    return cbQosObjectTable

# end def get_cbQosObjectTable
# ---------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------
def get_cbQosPolicyMapTable(cbQosPolicyMapCfgEntries):
# ---------------------------------------------------------------------------------------

    logger.debug("in get_cbQosPolicyMapTable")

    # store the stuff in a pre-cooked dictionary
    cbQosPolicyMapTable = AutoVivification()

    for cbQosPolicyMapEntry in cbQosPolicyMapCfgEntries.keys():
        array = cbQosPolicyMapEntry.split('.')
        pName = array[13];
        cbQosConfigIndex = array[14];

        if pName == '1':
            pVal = 'cbQosPolicyMapName'
        elif pName == '2':
            pVal = 'cbQosPolicyMapDesc'
        else:
            pVal = pName

        cbQosPolicyMapTable[cbQosConfigIndex][pVal] = cbQosPolicyMapCfgEntries[cbQosPolicyMapEntry]

    return cbQosPolicyMapTable

# end def get_cbQosPolicyMapTable
# ---------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------
def get_cbQosCMCfgTable(cbQosCMCfgEntries):
# ---------------------------------------------------------------------------------------

    logger.debug("in get_cbQosCMCfgTable")

    # store the stuff in a pre-cooked dictionary
    cbQosCMCfgTable = AutoVivification()

    for cbQosCMEntry in cbQosCMCfgEntries.keys():
        array = cbQosCMEntry.split('.')
        pName = array[13];
        cbQosConfigIndex = array[14];

        if pName == '1':
            pVal = 'cbQosCMName'
        elif pName == '2':
            pVal = 'cbQosCMDesc'
        elif pName == '3':
            pVal = 'cbQosCMInfo'
        else:
            pVal = pName

      	cbQosCMCfgTable[cbQosConfigIndex][pVal] = cbQosCMCfgEntries[cbQosCMEntry]

    return cbQosCMCfgTable

# end def get_cbQosCMCfgTable(cbQosCMCfgEntries):
# ---------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------
def get_cbQosQueueingCfgTable(cbQosQueueingCfgEntries):
# ---------------------------------------------------------------------------------------

    logger.debug("in get_cbQosQueueingCfgTable")

    # store the stuff in a pre-cooked dictionary
    cbQosQueueingCfgTable = AutoVivification()

    for cbQosQueueingCfgEntry in cbQosQueueingCfgEntries.keys():
        array = cbQosQueueingCfgEntry.split('.')
        pName = array[13];
        cbQosConfigIndex = array[14];

        if pName == '1':
            pVal = 'cbQosQueueingCfgBandwidth'
        elif pName == '2':
            pVal = 'cbQosQueueingCfgBandwidthUnits'
        elif pName == '3':
            pVal = 'cbQosQueueingCfgFlowEnabled'
        elif pName == '4':
            pVal = 'cbQosQueueingCfgPriorityEnabled'
        elif pName == '5':
            pVal = 'cbQosQueueingCfgAggregateQSize'
        elif pName == '6':
            pVal = 'cbQosQueueingCfgIndividualQSize'
        elif pName == '7':
            pVal = 'cbQosQueueingCfgDynamicQNumber'
        elif pName == '8':
            pVal = 'cbQosQueueingCfgPrioBurstSize'
        elif pName == '9':
            pVal = 'cbQosQueueingCfgQLimitUnits'
        elif pName == '10':
            pVal = 'cbQosQueueingCfgAggregateQLimit'
        elif pName == '11':
            pVal = 'cbQosQueueingCfgAggrQLimitTime'
        elif pName == '12':
            pVal = 'cbQosQueueingCfgPriorityLevel'
        else:
            pVal = pName

        cbQosQueueingCfgTable[cbQosConfigIndex][pVal] = cbQosQueueingCfgEntries[cbQosQueueingCfgEntry]

    return cbQosQueueingCfgTable

# end def get_cbQosQueueingCfgTable
# ---------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------
def get_cbQosTSCfgTable(cbQosTSCfgEntries):
# ---------------------------------------------------------------------------------------

    logger.debug("in get_cbQosTSCfgTable")

    # store the stuff in a pre-cooked dictionary
    cbQosTSCfgTable = AutoVivification()

    for cbQosTSCfgEntry in cbQosTSCfgEntries.keys():
        array = cbQosTSCfgEntry.split('.')
        pName = array[13];
        cbQosConfigIndex = array[14];

        if pName == '1':
            pVal = 'cbQosTSCfgRate'
        elif pName == '2':
            pVal = 'cbQosTSCfgBurstSize'
        elif pName == '3':
            pVal = 'cbQosTSCfgExtBurstSize'
        elif pName == '4':
            pVal = 'cbQosTSCfgAdaptiveEnabled'
        elif pName == '5':
            pVal = 'cbQosTSCfgAdaptiveRate'
        elif pName == '6':
            pVal = 'cbQosTSCfgLimitType'
        elif pName == '7':
            pVal = 'cbQosTSCfgRateType'
        elif pName == '8':
            pVal = 'cbQosTSCfgPercentRateValue'
        elif pName == '9':
            pVal = 'cbQosTSCfgBurstTime'
        elif pName == '10':
            pVal = 'cbQosTSCfgExtBurstTime'
        elif pName == '11':
            pVal = 'cbQosTSCfgRate64'
        elif pName == '12':
            pVal = 'cbQosTSCfgBurstSize64'
        elif pName == '13':
            pVal = 'cbQosTSCfgExtBurstSize64'
        else:
            pVal = pName

        cbQosTSCfgTable[cbQosConfigIndex][pVal] = cbQosTSCfgEntries[cbQosTSCfgEntry]

    return cbQosTSCfgTable

# end def get_cbQosTSCfgTable
# ---------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------
def get_cbQosPoliceCfgTable(cbQosPoliceCfgEntries):
# ---------------------------------------------------------------------------------------

    logger.debug("in get_cbQosPoliceCfgTable")

    # store the stuff in a pre-cooked dictionary
    cbQosPoliceCfgTable = AutoVivification()

    for cbQosPoliceCfgEntry in cbQosPoliceCfgEntries.keys():
        array = cbQosPoliceCfgEntry.split('.')
        pName = array[13];
        cbQosConfigIndex = array[14];

        if pName == '1':
            pVal = 'cbQosPoliceCfgRate'
        elif pName == '2':
            pVal = 'cbQosPoliceCfgBurstSize'
        elif pName == '3':
            pVal = 'cbQosPoliceCfgExtBurstSize'
        elif pName == '4':
            pVal = 'cbQosPoliceCfgConformAction'
        elif pName == '5':
            pVal = 'cbQosPoliceCfgConformSetValue'
        elif pName == '6':
            pVal = 'cbQosPoliceCfgExceedAction'
        elif pName == '7':
            pVal = 'cbQosPoliceCfgExceedSetValue'
        elif pName == '8':
            pVal = 'cbQosPoliceCfgViolateAction'
        elif pName == '9':
            pVal = 'cbQosPoliceCfgViolateSetValue'
        elif pName == '10':
            pVal = 'cbQosPoliceCfgPir'
        elif pName == '11':
            pVal = 'cbQosPoliceCfgRate64'
        elif pName == '12':
            pVal = 'cbQosPoliceCfgRateType'
        elif pName == '13':
            pVal = 'cbQosPoliceCfgPercentRateValue'
        elif pName == '14':
            pVal = 'cbQosPoliceCfgPercentPirValue'
        elif pName == '15':
            pVal = 'cbQosPoliceCfgCellRate'
        elif pName == '16':
            pVal = 'cbQosPoliceCfgCellPir'
        elif pName == '17':
            pVal = 'cbQosPoliceCfgBurstCell'
        elif pName == '18':
            pVal = 'cbQosPoliceCfgExtBurstCell'
        elif pName == '19':
            pVal = 'cbQosPoliceCfgBurstTime'
        elif pName == '20':
            pVal = 'cbQosPoliceCfgExtBurstTime'
        elif pName == '21':
            pVal = 'cbQosPoliceCfgCdvt'
        elif pName == '22':
            pVal = 'cbQosPoliceCfgConformColor'
        elif pName == '23':
            pVal = 'cbQosPoliceCfgExceedColor'
        elif pName == '24':
            pVal = 'cbQosPoliceCfgConditional'
        else:
            pVal = pName

        cbQosPoliceCfgTable[cbQosConfigIndex][pVal] = cbQosPoliceCfgEntries[cbQosPoliceCfgEntry]

    return cbQosPoliceCfgTable

# end def get cbQosPoliceCfgTable
# ---------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------
# parse cbQosObjectsTable to find the list of indices having a certain parent,
# type and top-index. Used to build the object hierarchy
#
def get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, objectType, parent):
# ---------------------------------------------------------------------------------------

    indices = []
    for cbQosObjectsTable_idx in cbQosObjectsTable[cbQosObjectsTable_top_idx]['QosObjectsEntry']:
        if  cbQosObjectsTable[cbQosObjectsTable_top_idx]['QosObjectsEntry'][cbQosObjectsTable_idx]['cbQosObjectsType']        == str(objectType) \
        and cbQosObjectsTable[cbQosObjectsTable_top_idx]['QosObjectsEntry'][cbQosObjectsTable_idx]['cbQosParentObjectsIndex'] == str(parent):
            indices.append(cbQosObjectsTable_idx)

    return indices

# end def get_indices


# ---------------------------------------------------------------------------------------
def get_cbQosConfigIndex(top_idx, obj_idx):
# ---------------------------------------------------------------------------------------

    return cbQosObjectsTable[top_idx]['QosObjectsEntry'][obj_idx]['cbQosConfigIndex']


# ---------------------------------------------------------------------------------------
def get_policymap_name(idx):
# ---------------------------------------------------------------------------------------

    return cbQosPolicyMapCfgTable[idx]['cbQosPolicyMapName']


# ---------------------------------------------------------------------------------------
def get_classmap_name(idx):
# ---------------------------------------------------------------------------------------

    return cbQosCMCfgTable[idx]['cbQosCMName']


# ---------------------------------------------------------------------------------------
def get_policymap_direction(idx):
# ---------------------------------------------------------------------------------------

    return cbQosServicePolicyTable[idx]['cbQosPolicyDirection']


# ---------------------------------------------------------------------------------------
def get_bandwidth(idx):
# ---------------------------------------------------------------------------------------

    bandwidth = cbQosQueueingCfgTable[idx]['cbQosQueueingCfgBandwidth']
    unit = cbQosQueueingCfgTable[idx]['cbQosQueueingCfgBandwidthUnits']
    # we don't divide by 1'000, because the unit is already kbps.
    return (bandwidth, unit)


# ---------------------------------------------------------------------------------------
def get_police(idx):
# ---------------------------------------------------------------------------------------

    rate = cbQosPoliceCfgTable[idx]['cbQosPoliceCfgRate64']
    unit = cbQosPoliceCfgTable[idx]['cbQosPoliceCfgRateType']
    perc_rate = cbQosPoliceCfgTable[idx]['cbQosPoliceCfgPercentRateValue']
    if unit == '1':   # bps
        rate = str(int(rate) / 1000)
    return (rate, unit, perc_rate)


# ---------------------------------------------------------------------------------------
def get_shaping(idx):
# ---------------------------------------------------------------------------------------

    rate = cbQosTSCfgTable[idx]['cbQosTSCfgRate']
    unit = cbQosTSCfgTable[idx]['cbQosTSCfgRateType']
    if unit == '1':   # bps
        rate = str(int(rate) / 1000)
    return (rate, unit)


# ---------------------------------------------------------------------------------------
def get_interface(idx):

    interface_idx = cbQosServicePolicyTable[idx]['cbQosIfIndex']
    interface_name = interfaces[interface_idx]
    return (interface_idx, interface_name)


# ---------------------------------------------------------------------------------------
def get_full_oid(base_oid, policy_idx, obj_idx):

	return qos_oids[base_oid] + '.' + str(policy_idx) + '.' + str(obj_idx)


# ---------------------------------------------------------------------------------------
def format_nr(number):
# 1000000000 --> 1'000'000'000
# Python 2.7 has formats, but we are still under 2.6
# ---------------------------------------------------------------------------------------

    try:
        number = int(number)
        s = '%d' % number
        groups = []
        while s and s[-1].isdigit():
            groups.append(s[-3:])
            s = s[:-3]
        return s + "'".join(reversed(groups))

    except:
        return number


# ---------------------------------------------------------------------------------------
class AutoVivification(dict):
# ---------------------------------------------------------------------------------------
    # Implementation of perl's autovivification feature
    # http://stackoverflow.com/questions/635483/what-is-the-best-way-to-implement-nested-dictionaries-in-python
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------
# OID definitions
# ---------------------------------------------------------------------------------------

oids = {}
oids['ifDescr']                 = (1,3,6,1,2,1,2,2,1,2)
oids['cbQosServicePolicyEntry'] = (1,3,6,1,4,1,9,9,166,1,1,1,1)
oids['cbQosObjectsEntry']       = (1,3,6,1,4,1,9,9,166,1,5,1,1)
oids['cbQosPolicyMapCfgEntry']  = (1,3,6,1,4,1,9,9,166,1,6,1,1)
oids['cbQosCMCfgEntry']         = (1,3,6,1,4,1,9,9,166,1,7,1,1)
oids['cbQosQueueingCfgEntry']   = (1,3,6,1,4,1,9,9,166,1,9,1,1)
oids['cbQosPoliceCfgEntry']     = (1,3,6,1,4,1,9,9,166,1,12,1,1)
oids['cbQosTSCfgEntry']         = (1,3,6,1,4,1,9,9,166,1,13,1,1)

qos_oids = {}
qos_oids['cbQosCMPostPolicyByte64'] = '1.3.6.1.4.1.9.9.166.1.15.1.1.10'
qos_oids['cbQosCMDropPkt64']        = '1.3.6.1.4.1.9.9.166.1.15.1.1.14'


# ---------------------------------------------------------------------------------------
# a few lookup tables
# ---------------------------------------------------------------------------------------
policy_traffic_direction_names = {'1': 'input', '2': 'output'}
queueing_bandwidth_units = {'1': 'kbps', '2': '%', '3': '% remaining', '4': 'ratioRemaining'}
police_rate_types = {'1': 'kbps', '2': '%', '3': 'cps'}
shaping_rate_types = {'1': 'kbps', '2': '%', '3': 'cps', '4': 'perThousand', '5': 'perMillion'}
object_types = {'1': 'policymap',
                '2': 'classmap',
                '3': 'matchStatement',
                '4': 'queueing',
                '5': 'randomDetect',
                '6': 'trafficShaping',
                '7': 'police',
                '8': 'set',
                '9': 'compression',
                '10': 'ipslaMeasure',
                '11': 'account',
                'policymap':      '1',
                'classmap':       '2',
                'matchStatement': '3',
                'queueing':       '4',
                'randomDetect':   '5',
                'trafficShaping': '6',
                'police':         '7',
                'set':            '8',
                'compression':    '9',
                'ipslaMeasure':   '10',
                'account':        '11'}


# ---------------------------------------------------------------------------------------
# some global config values
# ---------------------------------------------------------------------------------------
port = 161

# ---------------------------------------------------------------------------------------
# logging
# ---------------------------------------------------------------------------------------
logfile = '/tmp/zenoss_qos_parser.log'
logger = logging.getLogger('qos-discovery')
hdlr = logging.FileHandler(logfile)
# we have the PID in each log entry to differentiate parallel processes writing to the log
formatter = logging.Formatter('%(asctime)s - %(process)d - %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
# avoid propagation to console
logger.propagate = False
#logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

logger.info("program start")

if pysnmp_version == '4.3.2':
    logger.info('pysnmp version : %s' % pysnmp_version)
else:
    logger.warn('Zenpack is only tested with pysnmp 4.3.2')

# get arguments
parser = OptionParser()
parser.add_option("-c", "--community",   dest="community",    default="",       help="read-only SNMP community")
parser.add_option("-d", "--device",      dest="device",       default="",       help="device name")
parser.add_option("-D", "--debug",       action="store_true", dest="debug",     default="",       help="debug mode")
(params, args) = parser.parse_args()
hostname = params.device
community = params.community
if hostname == '':
    logger.error("please pass a device as parameter using -d device")
    print "FATAL : please pass a device as parameter using -d device"
    sys.exit(1)
elif community == '':
    logger.error("please pass a comunity as parameter using -c community")
    print "FATAL : please pass a community as parameter using -c community"
    sys.exit(1)
else:
    logger.debug("device to parse : %s", hostname)

print 'device %s' % (hostname)
print ""

# debug mode on STDOUT
debug = params.debug

# initialize the pretty printer
if debug:
    pp = pprint.PrettyPrinter(indent=4)


# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------
# start by collecting all relevant OID tables from the device.
# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------


# get cbQosServicePolicyEntries and format it in cbQosServicePolicyTable
# ---------------------------------------------------------------------------------------

cbQosServicePolicyEntries = get_table(hostname, port, community, oids['cbQosServicePolicyEntry'])
cbQosServicePolicyTable = get_cbQosServicePolicyTable(cbQosServicePolicyEntries)
if debug:
    print 'cbQosServicePolicyTable'
    pp.pprint(cbQosServicePolicyTable)
    print "\n"


# get ifDescr
# ---------------------------------------------------------------------------------------

ifEntries = get_table(hostname, port, community, oids['ifDescr'])
ifEntriesTable = get_ifEntriesTable(ifEntries)
if debug:
    print 'ifEntriesTable'
    pp.pprint(ifEntriesTable)
    print "\n"


# get cbQosObjectsEntries
# ---------------------------------------------------------------------------------------

cbQosObjectsEntries = get_table(hostname, port, community, oids['cbQosObjectsEntry'])
cbQosObjectsTable = get_cbQosObjectTable(cbQosObjectsEntries)
if debug:
    print 'cbQosObjectsTable'
    pp.pprint(cbQosObjectsTable)
    print "\n"


# get cbQosPolicyMapCfgEntry
# ---------------------------------------------------------------------------------------

cbQosPolicyMapCfgEntries = get_table(hostname, port, community, oids['cbQosPolicyMapCfgEntry'])
cbQosPolicyMapCfgTable = get_cbQosPolicyMapTable(cbQosPolicyMapCfgEntries)
if debug:
    print 'cbQosPolicyMapCfgTable'
    pp.pprint(cbQosPolicyMapCfgTable)
    print "\n"


# get cbQosCMCfgEntry
# ---------------------------------------------------------------------------------------
cbQosCMCfgEntries = get_table(hostname, port, community, oids['cbQosCMCfgEntry'])
cbQosCMCfgTable = get_cbQosCMCfgTable(cbQosCMCfgEntries)
if debug:
    print 'cbQosCMCfgTable'
    pp.pprint(cbQosCMCfgTable)
    print "\n"


# get cbQosQueueingCfgEntry
# ---------------------------------------------------------------------------------------
cbQosQueueingCfgEntries = get_table(hostname, port, community, oids['cbQosQueueingCfgEntry'])
cbQosQueueingCfgTable = get_cbQosQueueingCfgTable(cbQosQueueingCfgEntries)
if debug:
    print 'cbQosQueueingCfgTable'
    pp.pprint(cbQosQueueingCfgTable)
    print "\n"


# get cbQosTSCfgEntry (shaping config)
# ---------------------------------------------------------------------------------------
cbQosTSCfgEntries = get_table(hostname, port, community, oids['cbQosTSCfgEntry'])
cbQosTSCfgTable = get_cbQosTSCfgTable(cbQosTSCfgEntries)
if debug:
    print 'cbQosTSCfgTable'
    pp.pprint(cbQosTSCfgTable)
    print "\n"


# get cbQosPoliceCfgEntry
# ---------------------------------------------------------------------------------------
cbQosPoliceCfgEntries = get_table(hostname, port, community, oids['cbQosPoliceCfgEntry'])
cbQosPoliceCfgTable = get_cbQosPoliceCfgTable(cbQosPoliceCfgEntries)
if debug:
    print 'cbQosPoliceCfgTable'
    pp.pprint(cbQosPoliceCfgTable)
    print "\n"


# ---------------------------------------------------------------------------------------
# construct list of interfaces having QoS defined
# use a dict so we get auto-unification
# ---------------------------------------------------------------------------------------
logger.debug("get table of interfaces with QoS")
interfaces = {}
for cbQosPolicyIndex in cbQosServicePolicyTable.keys():
    logger.debug("cbQosPolicyIndex : %s", cbQosPolicyIndex)

    # get associated interface name
    interface_idx = cbQosServicePolicyTable[cbQosPolicyIndex]['cbQosIfIndex']
    interface_name = ifEntriesTable[interface_idx]
    logger.debug("interface idx = %s, name = %s" % (interface_idx, interface_name))
    interfaces[interface_idx] = interface_name

if debug:
    print 'interfaces'
    pp.pprint(interfaces)
    print "\n"


# ---------------------------------------------------------------------------------------
# prepare an interface table object to make later parsing easier
#
# each entry in InterfacesTable is built as:
#    key   -> interface-name
#    value -> array of service-policies indices
#    eg    'GigabitEthernet0/0' -> [16, 18]
#          'GigabitEthernet0/2' -> [50]
#
# two rounds to build the table, first the key->table, then fill each table
# ---------------------------------------------------------------------------------------
InterfacesTable = {}
for idx in cbQosServicePolicyTable:
	(interface_idx, interface_name) = get_interface(idx)
	InterfacesTable[interface_name] = []
for idx in cbQosServicePolicyTable:
	(interface_idx, interface_name) = get_interface(idx)
	InterfacesTable[interface_name].append(idx)


if debug:
	print '-------------------------------------'


# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------
# loop over the cbQosObjectsTable to build its hierarchy
# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------
logger.info("build the hierarchy of cbQosObjectsTable in ObjectsTable")

ObjectsTable = AutoVivification()

for cbQosObjectsTable_top_idx in cbQosObjectsTable.keys():

    # store the interface name
    (interface_idx, interface_name) = get_interface(cbQosObjectsTable_top_idx)
    ObjectsTable[cbQosObjectsTable_top_idx]['ifname'] = interface_name

    # first, find the top-level policy-maps, aka service policies attached to interfaces
    indices_L1 = get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['policymap'], '0')
    for idx_L1 in indices_L1:
        cbQosConfigIndex = get_cbQosConfigIndex(cbQosObjectsTable_top_idx, idx_L1)
        policymapname = get_policymap_name(cbQosConfigIndex)
        policymapdirection = policy_traffic_direction_names[get_policymap_direction(cbQosObjectsTable_top_idx)]
        ObjectsTable[cbQosObjectsTable_top_idx]['servicePolicyName']      = policymapname
        ObjectsTable[cbQosObjectsTable_top_idx]['servicePolicyDirection'] = policymapdirection
        ObjectsTable[cbQosObjectsTable_top_idx]['subclasses']             = {}

        # second, find the class-maps within the current service-policy
        indices_L2 = get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['classmap'], idx_L1)
        for idx_L2 in indices_L2:
            cbQosConfigIndex = get_cbQosConfigIndex(cbQosObjectsTable_top_idx, idx_L2)
            classmapname_L2 = get_classmap_name(cbQosConfigIndex)
            ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2] = {}

            # find the bandwidth info for this class-map
            indices_L2b = get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['queueing'], idx_L1)
            for idx_L2b in indices_L2b:
				cbQosConfigIndex = get_cbQosConfigIndex(cbQosObjectsTable_top_idx, idx_L2b)
				(bandwidth, units) = get_bandwidth(cbQosConfigIndex)
				ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['idx_L2']       = idx_L2
				ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['idx_L2b_bw']   = idx_L2b
				ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['bw']           = bandwidth
				ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['bw_unit']      = units
				ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['bw_unit_text'] = queueing_bandwidth_units[units]

            # find the police info for this class-map
            indices_L2b = get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['police'], idx_L1)
            for idx_L2b in indices_L2b:
				cbQosConfigIndex = get_cbQosConfigIndex(cbQosObjectsTable_top_idx, idx_L2b)
				(police_rate, police_rate_type, police_percent_rate) = get_police(cbQosConfigIndex)
				ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['idx_L2']                = idx_L2
				ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['idx_L2b_pol']           = idx_L2b
				ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['police_rate']           = police_rate
				ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['police_rate_type']      = police_rate_type
				ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['police_rate_type_text'] = police_rate_types[police_rate_type]
				ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['police_percent_rate']   = police_percent_rate

            # find the shaping info for this class-map
            indices_L2b = get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['trafficShaping'], idx_L2)
            for idx_L2b in indices_L2b:
				cbQosConfigIndex = get_cbQosConfigIndex(cbQosObjectsTable_top_idx, idx_L2b)
				(shape_rate, shape_type) = get_shaping(cbQosConfigIndex)
				ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['shape_rate']      = shape_rate
				ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['shape_type']      = shape_type
				ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['shape_type_text'] = shaping_rate_types[shape_type]
				ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['cfgidx']          = idx_L2

            # find the random-detect info for this class-map
            indices_L2b = get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['randomDetect'], idx_L2)
            for idx_L2b in indices_L2b:
				cbQosConfigIndex = get_cbQosConfigIndex(cbQosObjectsTable_top_idx, idx_L2b)
				ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['random_detect'] = True
				ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['cfgidx']        = idx_L2

            # third level : the policy-maps within the current class-map
            indices_L3 = get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['policymap'], idx_L2)
            for idx_L3 in indices_L3:
				cbQosConfigIndex = get_cbQosConfigIndex(cbQosObjectsTable_top_idx, idx_L3)
				policymapname_L3 = get_policymap_name(cbQosConfigIndex)
				ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['PolicyName']  = policymapname_L3
				ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses']  = {}

				# fourth level : the class-maps within the current policy-map
				indices_L4 = get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['classmap'], idx_L3)
				for idx_L4 in indices_L4:
					cbQosConfigIndex = get_cbQosConfigIndex(cbQosObjectsTable_top_idx, idx_L4)
					classmapname_L4 = get_classmap_name(cbQosConfigIndex)
					ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4] = {}

					# find the bandwidth info for this class-map
					indices_L5 = get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['queueing'], idx_L4)
					for idx_L5 in indices_L5:
						cbQosConfigIndex = get_cbQosConfigIndex(cbQosObjectsTable_top_idx, idx_L5)
						(bandwidth, units) = get_bandwidth(cbQosConfigIndex)
						ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['cfgidx']       = idx_L4
						ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['bw']           = bandwidth
						ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['bw_unit']      = units
						ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['bw_unit_text'] = queueing_bandwidth_units[units]

					# find the police info for this class-map
					indices_L5 = get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['police'], idx_L4)
					for idx_L5 in indices_L5:
						cbQosConfigIndex = get_cbQosConfigIndex(cbQosObjectsTable_top_idx, idx_L5)
						(police_rate, police_rate_type, police_percent_rate) = get_police(cbQosConfigIndex)
						ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['cfgidx']                = idx_L4
						ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['police_rate']           = police_rate
						ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['police_rate_type']      = police_rate_type
						ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['police_rate_type_text'] = police_rate_types[police_rate_type]
						ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['police_percent_rate']   = police_percent_rate

                    # find the shaping info for this class-map
					indices_L5 = get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['trafficShaping'], idx_L4)
					for idx_L5 in indices_L5:
						cbQosConfigIndex = get_cbQosConfigIndex(cbQosObjectsTable_top_idx, idx_L5)
						(shape_rate, shape_type) = get_shaping(cbQosConfigIndex)
						ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['shape_rate']      = shape_rate
						ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['shape_type']      = shape_type
						ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['shape_type_text'] = shaping_rate_types[shape_type]
						ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['cfgidx']          = idx_L4

                    # find the random-detect info for this class-map
					indices_L5 = get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['randomDetect'], idx_L4)
					for idx_L5 in indices_L5:
						cbQosConfigIndex = get_cbQosConfigIndex(cbQosObjectsTable_top_idx, idx_L5)
						ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['random_detect'] = True
						ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['cfgidx']        = idx_L4

                    # REMARK :
                    # we are now in double-nested classes :
                    # interface -> service-policy -> class-map -> policy-map -> class-map
                    # some CCIE's argue deeper recursion is indeed possible, but highly improbable, so we stop recursing here.


if debug:
	print 'ObjectsTable'
	pp.pprint(ObjectsTable)
	print '-------------------------------------'

if debug:
	print 'InterfacesTable'
	pp.pprint(InterfacesTable)
	print '-------------------------------------'


# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------
# present the results
# for each interface, we show the attached service-policy, then dig-down to the sub-objects
# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------

if debug:
	print '-------------------------------------'
	print '-------- RESULTS --------------------'
	print '-------------------------------------'

for interface_idx in interfaces:

	# each interface
	interface_name = interfaces[interface_idx]
	print "interface %s" % interface_name

	# for each service-policy bound to the current interface
	for ObjectsTable_idx in InterfacesTable[interface_name]:
		print "    service-policy : %s (%s)" % (ObjectsTable[ObjectsTable_idx]['servicePolicyName'], ObjectsTable[ObjectsTable_idx]['servicePolicyDirection'])

		# each class-map
		for class_map_L1 in ObjectsTable[ObjectsTable_idx]['subclasses']:
			print "        Class-map : %s" % (class_map_L1)

			# the shaping
			if 'shape_rate' in ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]:
				print "            shaping : %s %s" % (format_nr(ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['shape_rate']), ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['shape_type_text'])

			# the random-detect
			if 'random_detect' in ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]:
				print "            random-detect"

			# in case someone wants to graph something, here is how you get the OIDs
			if 'cfgidx' in ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]:
				obj_idx = ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['cfgidx']
				cbQosCMPostPolicyByte64_oid = get_full_oid('cbQosCMPostPolicyByte64', ObjectsTable_idx, obj_idx)
				cbQosCMDropPkt64_oid = get_full_oid('cbQosCMDropPkt64', ObjectsTable_idx, obj_idx)
				if debug:
					print "            cbQosCMPostPolicyByte64_oid = %s" % (cbQosCMPostPolicyByte64_oid)
					print "            cbQosCMDropPkt64_oid        = %s" % (cbQosCMDropPkt64_oid)

			# the policy in the map
			if 'PolicyName' in ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]:
				print "            policy-map : %s" % (ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['PolicyName'])

			# each class-map
			if 'subclasses' in ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]:
				for class_map_L2 in ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses']:
					print "                class-map : %s" % (class_map_L2)

					# bandwidth
					if 'bw' in ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]:
						print "                    bandwidth : %s %s" % (ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]['bw'], ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]['bw_unit_text'])

					# police
					if 'police_percent_rate' in ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]:
						print "                    police : %s %s" % (ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]['police_percent_rate'], ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]['police_rate_type_text'])

					# shaping
					if 'shape_rate' in ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]:
						print "                    shaping : %s %s" % (format_nr(ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]['shape_rate']), ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]['shape_type_text'])

					# the random-detect
					if 'random_detect' in ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]:
						print "                    random-detect"

					# in case someone wants to graph something, here is how you get the OIDs
					if 'cfgidx' in ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]:
						obj_idx = ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]['cfgidx']
						cbQosCMPostPolicyByte64_oid = get_full_oid('cbQosCMPostPolicyByte64', ObjectsTable_idx, obj_idx)
						cbQosCMDropPkt64_oid = get_full_oid('cbQosCMDropPkt64', ObjectsTable_idx, obj_idx)
						if debug:
							print "                    cbQosCMPostPolicyByte64_oid = %s" % (cbQosCMPostPolicyByte64_oid)
							print "                    cbQosCMDropPkt64_oid        = %s" % (cbQosCMDropPkt64_oid)

			print ""

logger.info("program end")
