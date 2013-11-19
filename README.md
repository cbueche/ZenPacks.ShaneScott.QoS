QoS ZenPack for Zenoss
======================


Features
--------

- Monitor the Cisco CBQoS for all Cisco router models.
- Shows the service policy for each interface.
- List the QoS classes for each policy.
- As the policies and classes might be recursive, the QoS classes recurse two levels deep (interface → service-policy → classes → policy → classes).
- The traffic (bits/s) and drops for every class are graphed.
- Only output traffic is shown.


Limitations
-----------

- only 2 levels deep, usually enough even for the most evolved QoS implementations. If you need a third level, it might be time to upgrade your CCIE certification :-)
- maybe not correct / complete listings of classes and policies, the network at hand during implementation was quite standardized.
- no stacked views showing all classes of one interfaces. The CBQoS MIB is ridiculously complicated and implementing stacked traffic classes is hard when the ground (indices) are moving under your feet.


Definitions
-----------

- CBQoS (Class Based Quality of Service) is a Cisco feature set that is part of IOS 12.4(4)T and above. This provides information about the QoS policies applied and class based traffic patterns within an enterprise network.
- Zenoss is a monitoring software.
- ZenPacks are Zenoss extensions.

MIBs
----

- The ZenPack uses the [CISCO-CLASS-BASED-QOS-MIB](http://tools.cisco.com/Support/SNMP/do/BrowseOID.do?objectInput=1.3.6.1.4.1.9.9.166&translate=Translate&submitValue=SUBMIT) at 1.3.6.1.4.1.9.9.166 to model the policies and classes of network interfaces.
- The ZenPack does not use the CISCO-CBP-TARGET-MIB at 1.3.6.1.4.1.9.9.533, because its availability on Cisco devices is uncommon.


Assumptions
-----------

The following IOS commands might be present on modeled devices to allow for long-term indices persistence, but their presence are not guaranteed. The modeling does not dependent on them.

    snmp-server ifindex persist
    snmp mib persist cbqos


Installation
------------

    cd ~/tmp
    git clone FIXME
    zenpack --install FIXME
    zenoss restart


Post install notes
------------------

- The zenpack will install pysnmp automatically.
- Device class /Devices/Network/Router/QoS will be created
- The QoS modeller QoSClass will be added. zSnmpVer is also set to v2c. Devices must be polled using v2c or v3.
- if the QoSClass container does not appear under 'Components' on the device page, see the "troubleshooting" section below.


Usage
-----

- Devices must be polled using v2c or v3.
- QoS devices do not need to be in this /Devices/Network/Router/QoS specifically, but do need to be somewhere under /Devices/Network.
- A QoS device can be modeled by adding the modeller QoSClass to that device or devices DeviceClass.
- A QoS device that modeled OK will show 'QoS Class Maps' on the device component list.
- 'Class Maps' provides all graphing. Graphs 'Throughput' and 'Drops' provided.
- All object persistence based on naming and attributes rather than ifIndex.


Troubleshooting
---------------

If the QoSClass container does not appear under 'Components' on the device page, it might be because the object relations were not built correctly at init time. Fix them with this code:

    zendmd
    for d in dmd.Devices.getSubDevices():
        d.os.buildRelations()

    commit()

    zenoss restart

The modeling can be debugged on the command-line. Be aware that the output is not easy to interpret, as the QoS MIB is complex.

    zenmodeler run -v 10 -d devicename


Debugging the QoS configuration parsing
---------------------------------------

Deeply buried within the Zenpack is a script I wrote to understand QoS and how Cisco models it in its MIB. The script can be invoked by something like this (adapt the path accordingly):

    $ZENHOME/ZenPacks/ZenPacks.ShaneScott.QoS.egg/ZenPacks/ShaneScott/QoS/utils/qos_parser.py -c community -d device

It produces a hierarchical view of service-policies attached to interfaces, including the underlying classes and policies. The code of the ZenPack modeler is an adaptation of this script.


Dependencies
------------

- Zenoss 3.2.1 (tested)
- Zenoss 4.x (maybe working, to be confirmed)
- pysnmp 4.x (in Zenoss environment)


Authors
-------

- Shane William Scott did the initial 1.0 implementation
- Charles Bueche adapted the code and fixed some issues, eg the modeling for the Cisco ASR routers.

