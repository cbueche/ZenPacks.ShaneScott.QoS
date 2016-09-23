#
# ZenPacks.ShaneScott.QoS/ZenPacks/ShaneScott/QoS/QoS.py
#

import sys
from pysnmp.hlapi import *
from pysnmp import __version__ as pysnmp_version
from optparse import OptionParser
import logging

class QoSmodel():

    # a function to run a snmpbulkget on an OID, and get a dictionary back
    # ---------------------------------------------------------------------------------------
    def get_table(self, hostname, port, community, oid):
    # ---------------------------------------------------------------------------------------

        mylog = logging.getLogger("zen.ZenQoSmodel")

        # some tuning that might need adjustements
        nonRepeaters = 0
        maxRepetitions = 20

        mylog.debug('get_table : hostname=%s, port=%s, community=%s, oid=%s', hostname, port, 'community', oid)
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
                mylog.error('error : %s', errorIndication)
                return {}
            else:
                if errorStatus:
                    mylog.error('%s at %s\n' % (
                        errorStatus.prettyPrint(),
                        errorIndex and varBinds[-1][int(errorIndex)-1] or '?'
                        ))
                    return {}
                else:
                    # sucessful walk. Store the index and values in a dictionary
                    for varBind in varBinds:
                        table[varBind[0].prettyPrint()] = varBind[1].prettyPrint()

        return table

    def get_cbQosServicePolicyTable(self, cbQosServicePolicyEntries):
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

    def get_ifEntriesTable(self, ifEntries):
        ifEntriesTable = {}
        for ifEntry in ifEntries.keys():
            array = ifEntry.split('.')
            ifEntryIndex = array[10]

            ifEntriesTable[ifEntryIndex] = ifEntries[ifEntry]

        return ifEntriesTable

    def get_cbQosObjectTable(self, cbQosObjectsEntries):
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

    def get_cbQosPolicyMapTable(self, cbQosPolicyMapCfgEntries):
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

    def get_cbQosCMCfgTable(self, cbQosCMCfgEntries):
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

    def get_cbQosQueueingCfgTable(self, cbQosQueueingCfgEntries):
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

    def get_cbQosTSCfgTable(self, cbQosTSCfgEntries):
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

    def get_cbQosPoliceCfgTable(self, cbQosPoliceCfgEntries):
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

    def get_interfaces(self, cbQosServicePolicyTable, ifEntriesTable):
		interfaces = {}
		for cbQosPolicyIndex in cbQosServicePolicyTable.keys():
			interface_idx = cbQosServicePolicyTable[cbQosPolicyIndex]['cbQosIfIndex']
			interface_name = ifEntriesTable[interface_idx]
			interfaces[interface_idx] = interface_name
		return interfaces

    def get_indices(self, cbQosObjectsTable, cbQosObjectsTable_top_idx, objectType, parent):
        """ parse cbQosObjectsTable to find the list of indices having a certain parent,
            type and top-index. Used to build the object hierarchy
        """
        indices = []
        for cbQosObjectsTable_idx in cbQosObjectsTable[cbQosObjectsTable_top_idx]['QosObjectsEntry']:
            if  cbQosObjectsTable[cbQosObjectsTable_top_idx]['QosObjectsEntry'][cbQosObjectsTable_idx]['cbQosObjectsType']        == str(objectType) \
            and cbQosObjectsTable[cbQosObjectsTable_top_idx]['QosObjectsEntry'][cbQosObjectsTable_idx]['cbQosParentObjectsIndex'] == str(parent):
                indices.append(cbQosObjectsTable_idx)

        return indices

    def get_cbQosConfigIndex(self, cbQosObjectsTable, top_idx, obj_idx):
        return cbQosObjectsTable[top_idx]['QosObjectsEntry'][obj_idx]['cbQosConfigIndex']

    def get_policymap_name(self, cbQosPolicyMapCfgTable, idx):
        return cbQosPolicyMapCfgTable[idx]['cbQosPolicyMapName']

    def get_classmap_name(self, cbQosCMCfgTable, idx):
        return cbQosCMCfgTable[idx]['cbQosCMName']

    def get_policymap_direction(self, cbQosServicePolicyTable, idx):
        return cbQosServicePolicyTable[idx]['cbQosPolicyDirection']

    def get_bandwidth(self, cbQosQueueingCfgTable, idx):
    	bandwidth = cbQosQueueingCfgTable[idx]['cbQosQueueingCfgBandwidth']
    	unit = cbQosQueueingCfgTable[idx]['cbQosQueueingCfgBandwidthUnits']
        # we don't divide by 1'000, because the unit is already kbps.
        return (bandwidth, unit)

    def get_police(self, cbQosPoliceCfgTable, idx):
        rate = cbQosPoliceCfgTable[idx]['cbQosPoliceCfgRate64']
        unit = cbQosPoliceCfgTable[idx]['cbQosPoliceCfgRateType']
        perc_rate = cbQosPoliceCfgTable[idx]['cbQosPoliceCfgPercentRateValue']
        if unit == '1':   # bps
            rate = str(int(rate) / 1000)
        return (rate, unit, perc_rate)

    def get_shaping(self, cbQosTSCfgTable, idx):
        rate = cbQosTSCfgTable[idx]['cbQosTSCfgRate']
        unit = cbQosTSCfgTable[idx]['cbQosTSCfgRateType']
        if unit == '1':   # bps
            rate = str(int(rate) / 1000)
        return (rate, unit)

    def get_interface(self, cbQosServicePolicyTable, interfaces, idx):
        interface_idx = cbQosServicePolicyTable[idx]['cbQosIfIndex']
        interface_name = interfaces[interface_idx]
        return (interface_idx, interface_name)

    def get_full_oid(self, base_oid, policy_idx, obj_idx):
        return qos_oids[base_oid] + '.' + str(policy_idx) + '.' + str(obj_idx)

    # ---------------------------------------------------------------------------------------
    def format_nr(self, number):
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


class AutoVivification(dict):
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value
