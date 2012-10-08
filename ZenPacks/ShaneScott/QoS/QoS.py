import sys
import logging
import pprint
from pysnmp.entity.rfc3413.oneliner import cmdgen
from optparse import OptionParser

class QoSmodel():
    def get_table(self, hostname, port, community, oid):
        errorIndication, errorStatus, errorIndex, varBindTable = cmdgen.CommandGenerator().nextCmd(cmdgen.CommunityData('my-agent', community), cmdgen.UdpTransportTarget((hostname, port)), oid)

        if errorIndication:
            logger.critical('error : %s', errorIndication)
            print "FATAL 1, exit"
            sys.exit(1)
        else:
            if errorStatus:
                logger.critical('%s at %s\n' % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBindTable[-1][int(errorIndex)-1] or '?'
                    ))
                sys.exit(1)
                print "FATAL 2, exit"
            else:
                # sucessful walk. Store the index and values in a dictionary
                table = {}
                for varBindTableRow in varBindTable:
                    for name, val in varBindTableRow:
                        table[name.prettyPrint()] = val.prettyPrint()
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

    def get_cbQosMatchStmtCfgTable(self, cbQosMatchStmtCfgEntries):
        cbQosMatchStmtTable = AutoVivification()

        for cbQosMatchStmtEntry in cbQosMatchStmtCfgEntries.keys():
            array = cbQosMatchStmtEntry.split('.')
            pName = array[13];
            cbQosConfigIndex = array[14];

            if pName == '1':
                pVal = 'cbQosMatchStmtName'
            elif pName == '2':
                pVal = 'cbQosMatchStmtInfo'
            else:
                pVal = pName

            cbQosMatchStmtTable[cbQosConfigIndex][pVal] = cbQosMatchStmtCfgEntries[cbQosMatchStmtEntry]

        return cbQosMatchStmtTable

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

    def get_bandwidth(self, cbQosPolicyIndex, cbQosObjectsIndex_param, cbQosObjectsTable, cbQosQueueingCfgTable):
        bandwidth = 0
        units = 1
        for cbQosObjectsIndex in cbQosObjectsTable[cbQosPolicyIndex]['QosObjectsEntry']:
            if cbQosObjectsTable[cbQosPolicyIndex]['QosObjectsEntry'][cbQosObjectsIndex]['cbQosObjectsType'] == '4' \
                and cbQosObjectsTable[cbQosPolicyIndex]['QosObjectsEntry'][cbQosObjectsIndex]['cbQosParentObjectsIndex'] == cbQosObjectsIndex_param:

                    bandwidth = cbQosQueueingCfgTable[cbQosObjectsTable[cbQosPolicyIndex]['QosObjectsEntry'][cbQosObjectsIndex]['cbQosConfigIndex']]['cbQosQueueingCfgBandwidth']
                    units = cbQosQueueingCfgTable[cbQosObjectsTable[cbQosPolicyIndex]['QosObjectsEntry'][cbQosObjectsIndex]['cbQosConfigIndex']]['cbQosQueueingCfgBandwidthUnits']
                    break

        return (bandwidth, units)

    def get_police(self, cbQosPolicyIndex, cbQosObjectsIndex_param, cbQosObjectsTable, cbQosPoliceCfgTable):
        cbQosPoliceCfgRate64 = 0
        cbQosPoliceCfgRateType = 1
        cbQosPoliceCfgPercentRateValue = 0
        for cbQosObjectsIndex in cbQosObjectsTable[cbQosPolicyIndex]['QosObjectsEntry']:
            if cbQosObjectsTable[cbQosPolicyIndex]['QosObjectsEntry'][cbQosObjectsIndex]['cbQosObjectsType'] == '7' \
                and cbQosObjectsTable[cbQosPolicyIndex]['QosObjectsEntry'][cbQosObjectsIndex]['cbQosParentObjectsIndex'] == cbQosObjectsIndex_param:

                    cbQosPoliceCfgRate64 = int(cbQosPoliceCfgTable[cbQosObjectsTable[cbQosPolicyIndex]['QosObjectsEntry'][cbQosObjectsIndex]['cbQosConfigIndex']]['cbQosPoliceCfgRate64'])
                    if cbQosPoliceCfgRate64 > 0:
                        cbQosPoliceCfgRate64 = cbQosPoliceCfgRate64 / 1000

                    cbQosPoliceCfgRateType = cbQosPoliceCfgTable[cbQosObjectsTable[cbQosPolicyIndex]['QosObjectsEntry'][cbQosObjectsIndex]['cbQosConfigIndex']]['cbQosPoliceCfgRateType']
                    cbQosPoliceCfgPercentRateValue = cbQosPoliceCfgTable[cbQosObjectsTable[cbQosPolicyIndex]['QosObjectsEntry'][cbQosObjectsIndex]['cbQosConfigIndex']]['cbQosPoliceCfgPercentRateValue']
                    break

        return (int(cbQosPoliceCfgRate64), int(cbQosPoliceCfgRateType), int(cbQosPoliceCfgPercentRateValue))

class AutoVivification(dict):
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value
