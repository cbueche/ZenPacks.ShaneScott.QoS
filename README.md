QoS ZenPack for Zenoss
======================


Status
------

I'm new in writing ZenPacks, so this piece of software will most probably hoose your precious Zenoss installation. Handle with care, consider it as alpha-quality, and feel free to submit patches.


Features
--------

- Monitor the Cisco CBQoS for all Cisco router models.
- Shows the service policy for each interface.
- List the QoS classes for each policy.
- As the policies and classes might be recursive, the QoS classes recurse two levels deep (interface → service-policy → classes → policy → classes).
- The traffic (kbits/s) and drops for every class are graphed.
- Only output traffic is shown.


Screenshots
-----------

Everyone wants [screenshots](http://www.netnea.com/cms/2013/11/19/qos-parsing-on-cisco-routers/).


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
    git clone https://github.com/cbueche/ZenPacks.ShaneScott.QoS.git
    zenpack --install ZenPacks.ShaneScott.QoS
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

If this break down with DB-conflict errors, try to stop zenmodeler and retry.

The modeling can be debugged on the command-line. Be aware that the output is not easy to interpret, as the QoS MIB is complex.

    zenmodeler run -v 10 -d devicename


Debugging the QoS configuration parsing
---------------------------------------

Deeply buried within the Zenpack distribution is a script I wrote to understand QoS and how Cisco models it in its MIB. The script can be invoked by something like this (adapt the path accordingly and/or copy the script to whatewer sane location):

    $ZENHOME/ZenPacks/ZenPacks.ShaneScott.QoS-1.3.1-py2.6.egg/ZenPacks/ShaneScott/QoS/bin/qos_parser.py -c community -d device

It produces a hierarchical view of service-policies attached to interfaces, including the underlying classes and policies. The code of the ZenPack modeler is an adaptation of this script.


Removal / un-installation
-------------------------

I'm not sure the ZenPack removal would remove everything and do the necessary cleanup. Maybe you need some manual cleanup, eg I had to do this two or three times, plus a reindex().

    zendmd
    for d in dmd.Devices.getSubDevices():
        d.os.buildRelations()

    commit()

Nevertheless, there is a remaining issue: after ZenPack removal, ClassMap entries persist in the Component parts of devices, producing a KeyError when clicked. That is now nice, and ideas/patches to fix this issue are very welcome.


Dependencies
------------

- Zenoss 3.2.1 (tested)
- Zenoss 4.x (maybe working, to be confirmed)
- pysnmp 4.x (in Zenoss environment)


Development
-----------

`Vagrantfile` and `dependency_manager.rb` are used solely during the Zenpack development.


Authors
-------

- [Shane William Scott](http://www.shanewilliamscott.com/) did the initial 1.0 implementation. Kudos for his Zenoss skills and ZenPack-fu, Shane rocks !
- [Charles Bueche](http://www.netnea.com/cms/netnea-the-team/charles-bueche/) adapted the code and fixed some issues, eg the modeling for the Cisco ASR routers.
