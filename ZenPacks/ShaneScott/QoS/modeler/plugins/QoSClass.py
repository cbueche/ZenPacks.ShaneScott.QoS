import Globals
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, MultiArgs
from ZenPacks.ShaneScott.QoS.QoS import QoSmodel, AutoVivification
from struct import *
import sys
import string
import subprocess

class QoSClass(PythonPlugin):

    ZENPACKID = 'ZenPacks.ShaneScott.QoS'

    transport = "python"
    maptype = 'QoSMap'
    relname = 'classes'
    compname = "os"
    modname = 'ZenPacks.ShaneScott.QoS.ClassMap'
    deviceProperties = PythonPlugin.deviceProperties + ('zSnmpCommunity', 'zSnmpPort')

    def collect(self, device, log):
        oids = {}
        modeler = QoSmodel()

        oids['ifDescr'] = (1,3,6,1,2,1,2,2,1,2)
        oids['cbQosServicePolicyEntry'] = (1,3,6,1,4,1,9,9,166,1,1,1,1)
        oids['cbQosObjectsEntry'] = (1,3,6,1,4,1,9,9,166,1,5,1,1)
        oids['cbQosPolicyMapCfgEntry'] = (1,3,6,1,4,1,9,9,166,1,6,1,1)
        oids['cbQosCMCfgEntry'] = (1,3,6,1,4,1,9,9,166,1,7,1,1)
        oids['cbQosQueueingCfgEntry'] = (1,3,6,1,4,1,9,9,166,1,9,1,1)
        oids['cbQosTSCfgEntry'] = (1,3,6,1,4,1,9,9,166,1,13,1,1)
        oids['cbQosPoliceCfgEntry'] = (1,3,6,1,4,1,9,9,166,1,12,1,1)

        policy_traffic_direction_names = {'1': 'INPUT', '2': 'OUTPUT'}
        queueing_bandwidth_units = {'1': 'kbps', '2': '%', '3': '% remaining', '4': 'ratioRemaining'}
        police_rate_types = {'1': 'kbps', '2': '%', '3': 'cps', '4': 'perThousand', '5': 'perMillion'}
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

        port =  getattr(device, 'zSnmpPort', 161)
        hostname = device.manageIp
        community = getattr(device, 'zSnmpCommunity', 'public')

        ifEntries = modeler.get_table(hostname, port, community, oids['ifDescr'])
        ifEntriesTable = modeler.get_ifEntriesTable(ifEntries)
        cbQosServicePolicyEntries = modeler.get_table(hostname, port, community, oids['cbQosServicePolicyEntry'])
        cbQosServicePolicyTable = modeler.get_cbQosServicePolicyTable(cbQosServicePolicyEntries)
        cbQosObjectsEntries = modeler.get_table(hostname, port, community, oids['cbQosObjectsEntry'])
        cbQosObjectsTable = modeler.get_cbQosObjectTable(cbQosObjectsEntries)
        cbQosPolicyMapCfgEntries = modeler.get_table(hostname, port, community, oids['cbQosPolicyMapCfgEntry'])
        cbQosPolicyMapCfgTable = modeler.get_cbQosPolicyMapTable(cbQosPolicyMapCfgEntries)        
        cbQosCMCfgEntries = modeler.get_table(hostname, port, community, oids['cbQosCMCfgEntry'])
        cbQosCMCfgTable = modeler.get_cbQosCMCfgTable(cbQosCMCfgEntries)
        cbQosQueueingCfgEntries = modeler.get_table(hostname, port, community, oids['cbQosQueueingCfgEntry'])
        cbQosQueueingCfgTable = modeler.get_cbQosQueueingCfgTable(cbQosQueueingCfgEntries)
        cbQosTSCfgEntries = modeler.get_table(hostname, port, community, oids['cbQosTSCfgEntry'])
        cbQosTSCfgTable = modeler.get_cbQosTSCfgTable(cbQosTSCfgEntries)
        cbQosPoliceCfgEntries = modeler.get_table(hostname, port, community, oids['cbQosPoliceCfgEntry'])
        cbQosPoliceCfgTable = modeler.get_cbQosPoliceCfgTable(cbQosPoliceCfgEntries)

        # two interface tables to make below mappings easier
        interfaces = modeler.get_interfaces(cbQosServicePolicyTable, ifEntriesTable)
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
            (interface_idx, interface_name) = modeler.get_interface(cbQosServicePolicyTable, interfaces, idx)
            InterfacesTable[interface_name] = []
        for idx in cbQosServicePolicyTable:
            (interface_idx, interface_name) = modeler.get_interface(cbQosServicePolicyTable, interfaces, idx)
            InterfacesTable[interface_name].append(idx)

        # loop over the cbQosObjectsTable to build its hierarchy
        ObjectsTable = AutoVivification()
        for cbQosObjectsTable_top_idx in cbQosObjectsTable.keys():

            # store the interface name
            (interface_idx, interface_name) = modeler.get_interface(cbQosServicePolicyTable, interfaces, cbQosObjectsTable_top_idx)
            ObjectsTable[cbQosObjectsTable_top_idx]['ifname'] = interface_name

            # first, find the top-level policy-maps, aka service policies attached to interfaces
            indices_L1 = modeler.get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['policymap'], '0')
            for idx_L1 in indices_L1:
                cbQosConfigIndex = modeler.get_cbQosConfigIndex(cbQosObjectsTable, cbQosObjectsTable_top_idx, idx_L1)
                policymapname = modeler.get_policymap_name(cbQosPolicyMapCfgTable, cbQosConfigIndex)
                policymapdirection = policy_traffic_direction_names[modeler.get_policymap_direction(cbQosServicePolicyTable, cbQosObjectsTable_top_idx)]
                ObjectsTable[cbQosObjectsTable_top_idx]['servicePolicyName']      = policymapname
                ObjectsTable[cbQosObjectsTable_top_idx]['servicePolicyDirection'] = policymapdirection
                ObjectsTable[cbQosObjectsTable_top_idx]['subclasses']             = {}

                # second, find the class-maps within the current service-policy
                indices_L2 = modeler.get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['classmap'], idx_L1)
                for idx_L2 in indices_L2:
                    cbQosConfigIndex = modeler.get_cbQosConfigIndex(cbQosObjectsTable, cbQosObjectsTable_top_idx, idx_L2)
                    classmapname_L2 = modeler.get_classmap_name(cbQosCMCfgTable, cbQosConfigIndex)
                    ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2] = {}

                    # find the bandwidth info for this class-map
                    indices_L2b = modeler.get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['queueing'], idx_L1)
                    for idx_L2b in indices_L2b:
                        cbQosConfigIndex = modeler.get_cbQosConfigIndex(cbQosObjectsTable, cbQosObjectsTable_top_idx, idx_L2b)
                        (bandwidth, units) = modeler.get_bandwidth(cbQosQueueingCfgTable, cbQosConfigIndex)
                        ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['idx_L2']       = idx_L2
                        ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['idx_L2b_bw']   = idx_L2b
                        ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['bw']           = bandwidth
                        ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['bw_unit']      = units
                        ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['bw_unit_text'] = queueing_bandwidth_units[units]

                    # find the police info for this class-map
                    indices_L2b = modeler.get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['police'], idx_L1)
                    for idx_L2b in indices_L2b:
                        cbQosConfigIndex = modeler.get_cbQosConfigIndex(cbQosObjectsTable, cbQosObjectsTable_top_idx, idx_L2b)
                        (police_rate, police_rate_type, police_percent_rate) = modeler.get_police(cbQosPoliceCfgTable, cbQosConfigIndex)
                        ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['idx_L2']                = idx_L2
                        ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['idx_L2b_pol']           = idx_L2b
                        ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['police_rate']           = police_rate
                        ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['police_rate_type']      = police_rate_type
                        ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['police_rate_type_text'] = police_rate_types[police_rate_type]
                        ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['police_percent_rate']   = police_percent_rate

                    # find the shaping info for this class-map
                    indices_L2b = modeler.get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['trafficShaping'], idx_L2)
                    for idx_L2b in indices_L2b:
                        cbQosConfigIndex = modeler.get_cbQosConfigIndex(cbQosObjectsTable, cbQosObjectsTable_top_idx, idx_L2b)
                        (shape_rate, shape_type) = modeler.get_shaping(cbQosTSCfgTable, cbQosConfigIndex)
                        ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['shape_rate']      = shape_rate
                        ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['shape_type']      = shape_type
                        ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['shape_type_text'] = shaping_rate_types[shape_type]
                        ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['cfgidx']          = idx_L2

                    # find the random-detect info for this class-map
                    indices_L2b = modeler.get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['randomDetect'], idx_L2)
                    for idx_L2b in indices_L2b:
                        cbQosConfigIndex = modeler.get_cbQosConfigIndex(cbQosObjectsTable, cbQosObjectsTable_top_idx, idx_L2b)
                        ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['random_detect'] = True
                        ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['cfgidx']        = idx_L2

                    # third level : the policy-maps within the current class-map
                    indices_L3 = modeler.get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['policymap'], idx_L2)
                    for idx_L3 in indices_L3:
                        cbQosConfigIndex = modeler.get_cbQosConfigIndex(cbQosObjectsTable, cbQosObjectsTable_top_idx, idx_L3)
                        policymapname_L3 = modeler.get_policymap_name(cbQosPolicyMapCfgTable, cbQosConfigIndex)
                        ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['PolicyName']  = policymapname_L3
                        ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses']  = {}

                        # fourth level : the class-maps within the current policy-map
                        indices_L4 = modeler.get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['classmap'], idx_L3)
                        for idx_L4 in indices_L4:
                            cbQosConfigIndex = modeler.get_cbQosConfigIndex(cbQosObjectsTable, cbQosObjectsTable_top_idx, idx_L4)
                            classmapname_L4 = modeler.get_classmap_name(cbQosCMCfgTable, cbQosConfigIndex)
                            ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4] = {}

                            # find the bandwidth info shaping_rate_types for this class-map
                            indices_L5 = modeler.get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['queueing'], idx_L4)
                            for idx_L5 in indices_L5:
                                cbQosConfigIndex = modeler.get_cbQosConfigIndex(cbQosObjectsTable, cbQosObjectsTable_top_idx, idx_L5)
                                (bandwidth, units) = modeler.get_bandwidth(cbQosQueueingCfgTable, cbQosConfigIndex)
                                ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['cfgidx']       = idx_L4
                                ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['bw']           = bandwidth
                                ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['bw_unit']      = units
                                ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['bw_unit_text'] = queueing_bandwidth_units[units]

                            # find the police info for this class-map
                            indices_L5 = modeler.get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['police'], idx_L4)
                            for idx_L5 in indices_L5:
                                cbQosConfigIndex = modeler.get_cbQosConfigIndex(cbQosObjectsTable, cbQosObjectsTable_top_idx, idx_L5)
                                (police_rate, police_rate_type, police_percent_rate) = modeler.get_police(cbQosPoliceCfgTable, cbQosConfigIndex)
                                ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['cfgidx']                = idx_L4
                                ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['police_rate']           = police_rate
                                ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['police_rate_type']      = police_rate_type
                                ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['police_rate_type_text'] = police_rate_types[police_rate_type]
                                ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['police_percent_rate']   = police_percent_rate

                            # find the shaping info for this class-map
                            indices_L5 = modeler.get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['trafficShaping'], idx_L4)
                            for idx_L5 in indices_L5:
                                cbQosConfigIndex = modeler.get_cbQosConfigIndex(cbQosObjectsTable, cbQosObjectsTable_top_idx, idx_L5)
                                (shape_rate, shape_type) = modeler.get_shaping(cbQosTSCfgTable, cbQosConfigIndex)
                                ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['shape_rate']      = shape_rate
                                ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['shape_type']      = shape_type
                                ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['shape_type_text'] = shaping_rate_types[shape_type]
                                ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['cfgidx']          = idx_L4

                            # find the random-detect info for this class-map
                            indices_L5 = modeler.get_indices(cbQosObjectsTable, cbQosObjectsTable_top_idx, object_types['randomDetect'], idx_L4)
                            for idx_L5 in indices_L5:
                                cbQosConfigIndex = modeler.get_cbQosConfigIndex(cbQosObjectsTable, cbQosObjectsTable_top_idx, idx_L5)
                                ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['random_detect'] = True
                                ObjectsTable[cbQosObjectsTable_top_idx]['subclasses'][classmapname_L2]['subclasses'][classmapname_L4]['cfgidx']        = idx_L4

                            # REMARK : 
                            # we are now in double-nested classes :
                            # interface -> service-policy -> class-map -> policy-map -> class-map
                            # some CCIE's argue deeper recursion is indeed possible, but highly improbable, so we stop recursing here.


        # now prepare the data to process, eg the list of class-maps and their attributes
        results = ''
        for interface_idx in interfaces:

            # each interface
            interface_name = interfaces[interface_idx]
            # print "interface %s" % interface_name

            # for each service-policy bound to the current interface
            for ObjectsTable_idx in InterfacesTable[interface_name]:
                # print "    service-policy : %s (%s)" % (ObjectsTable[ObjectsTable_idx]['servicePolicyName'], ObjectsTable[ObjectsTable_idx]['servicePolicyDirection'])

                # each class-map
                for class_map_L1 in ObjectsTable[ObjectsTable_idx]['subclasses']:
                    # print "        class-map : %s" % (class_map_L1)

                    # the shaping
                    # print "            shaping : %s %s" % (ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['shape_rate'], ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['shape_type_text'])

                    # the random-detect
                    if 'random_detect' in ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]:
                        pass
                    #     print "            random-detect"

                    # in case someone wants to graph something, here is how you get the OIDs
                    if 'cfgidx' in ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]:
                        obj_idx = ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['cfgidx']
                        # cbQosCMPostPolicyByte64_oid = get_full_oid('cbQosCMPostPolicyByte64', ObjectsTable_idx, obj_idx)
                        # cbQosCMDropPkt64_oid = get_full_oid('cbQosCMDropPkt64', ObjectsTable_idx, obj_idx)
                        bandwidth = ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1].get('shape_rate', '')
                        bandwidth_unit = ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1].get('shape_type_text', '')
                        service_policy = ObjectsTable[ObjectsTable_idx]['servicePolicyName']
                        policy_traffic_direction_name = ObjectsTable[ObjectsTable_idx]['servicePolicyDirection']
                        results = results + "\nCM1:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s" % (class_map_L1, bandwidth, bandwidth_unit, service_policy, interface_name, policy_traffic_direction_name, str(ObjectsTable_idx) + '.' + str(obj_idx), 'dummyCM', 'dummyPM', '', '')

                    # the policy in the map
                    # print "            policy-map : %s" % (ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['PolicyName'])

                    # each class-map
                    if 'subclasses' in ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]:
                        for class_map_L2 in ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses']:
                            # print "                class-map : %s" % (class_map_L2)

                            # bandwidth
                            # if 'bw' in ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]:
                                # pass
                                # print "                    bandwidth : %s %s" % (ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]['bw'], ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]['bw_unit_text'])

                            # police
                            # if 'police_percent_rate' in ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]:
                                # pass
                                # print "                    police : %s %s" % (ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]['police_percent_rate'], ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]['police_rate_type_text'])

                            # shaping
                            # if 'shape_rate' in ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]:
                                # pass
                                # print "                    shaping : %s %s" % (ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]['shape_rate'], ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]['shape_type_text'])

                            # the random-detect
                            # if 'random_detect' in ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]:
                                # pass
                                # print "                    random-detect"

                            # in case someone wants to graph something, here is how you get the OIDs
                            if 'cfgidx' in ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]:
                                obj_idx = ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]['cfgidx']
                                # cbQosCMPostPolicyByte64_oid = get_full_oid('cbQosCMPostPolicyByte64', ObjectsTable_idx, obj_idx)
                                # cbQosCMDropPkt64_oid = get_full_oid('cbQosCMDropPkt64', ObjectsTable_idx, obj_idx)
                                bandwidth = ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2].get('bw', '')
                                bandwidth_unit = ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2].get('bw_unit_text', '')
                                if 'random_detect' in ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2]:
                                    if bandwidth_unit == '':
                                        bandwidth_unit = 'RED'
                                    else:
                                        bandwidth_unit = bandwidth_unit + ' / RED'
                                policymapname = ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['PolicyName']
                                police_rate = ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2].get('police_percent_rate', '')
                                police_unit = ObjectsTable[ObjectsTable_idx]['subclasses'][class_map_L1]['subclasses'][class_map_L2].get('police_rate_type_text', '')
                                results = results + "\nCM3:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s" % (class_map_L2, bandwidth, bandwidth_unit, policymapname, interface_name, policy_traffic_direction_name, str(ObjectsTable_idx) + '.' + str(obj_idx), class_map_L1, service_policy, police_rate, police_unit)

        return results


    def process(self, device, results, log):
        """
        prepare the data for presentation
        """
        modeler = QoSmodel()
        log.info('processing %s for device %s', self.name(), device.id)
        rm = self.relMap()
        entries = str(results)
        for line in entries.split('\n'):
            if ':' in line:
                entry = line.split(':')
                if entry[0] == 'CM1' or  entry[0] == 'CM3':
                	#                                                                                                                   CM        name      BW        unit      parent    interf    direct    index     topCM     topPM     BW (pol.)  unit
                    log.info('val %s:%s Bandwidth:%s %s Parent:%s Interface:%s Direction:%s index:%s topCM:%s, topPM:%s, Pol-bw:%s %s', entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7], entry[8], entry[9], entry[10], entry[11])
                    om = self.objectMap()
                    # depending on hierarchy level, show top level or top+sub levels
                    if entry[0] == 'CM1':
                        #      interface        parent           class
                        omId = entry[5] + '^' + entry[4] + '^' + entry[1]
                    if entry[0] == 'CM3':
                        #      interface        policy-map       class-map        policy-map       class
                        omId = entry[5] + '^' + entry[9] + '^' + entry[8] + '^' + entry[4] + '^' + entry[1]
                    omId = omId.replace('\'','')
                    omId = omId.replace('/','_')
                    omId = omId.replace(' ','_')
                    omId = omId.replace('-','_')
                    omId = omId.replace('^','-')
                    om.id = self.prepId(omId)
                    instance = entry[1] + '-' + entry[5]
                    instance = instance.replace('\'','')
                    om.instance = instance
                    allocName = entry[1]
                    allocName = allocName.replace('\'','')
                    om.allocName = allocName
                    interface = entry[5]
                    interface = interface.replace('\'','')
                    om.parentInterface = interface
                    om.direction = entry[6]
                    om.allocBandwidth = modeler.format_nr(entry[2])
                    om.allocType = entry[3]
                    om.policeRate = modeler.format_nr(entry[10]) + ' ' + entry[11]
                    parentServicePolicy = entry[4] 
                    parentServicePolicy = parentServicePolicy.replace('\'','')
                    om.parentServicePolicy = parentServicePolicy
                    # what we display on the graph 
                    unifiedLegendList = omId.split('-')
                    unifiedLegendList.pop(0)
                    unifiedLegend = ' / '.join(unifiedLegendList)
                    om.unifiedLegend = unifiedLegend
                    om.snmpindex = str(entry[7])
                    rm.append(om)

        log.debug('rm %s', rm)
        return [rm]
