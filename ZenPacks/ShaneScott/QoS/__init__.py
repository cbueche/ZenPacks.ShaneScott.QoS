import Globals
import logging
import os
log = logging.getLogger('zen.ZenQoS')

import ZenPacks.ShaneScott.QoS
from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.ZenUtils.Utils import zenPath
from Products.ZenModel.ZenMenu import ZenMenu
from Products.Zuul.interfaces import ICatalogTool

from Products.ZenModel.OperatingSystem import OperatingSystem
from Products.ZenRelations.RelSchema import *


OperatingSystem._relations += (( "classes", ToManyCont(ToOne, "ZenPacks.ShaneScott.QoS.ClassMap", "os")),) 


def initialize(registrar):
        registrar.registerClass(
                ClassMap.ClassMap,
                permission='Add DMD Objects',
        )


class ZenPack(ZenPackBase):
    packZProperties =  []

    def install(self, app):
        super(ZenPack, self).install(app)
        self.symlinkPlugin()

        log.info('Adding QoS organizer')
        QoSOrg = app.dmd.Devices.createOrganizer('/Network/Router/QoS')
        plugins=[]
        networkOrg = app.dmd.findChild('Devices/Network/Router')
        for plugin in networkOrg.zCollectorPlugins:
            plugins.append(plugin)
        plugins.append('QoSClass')
        log.info('Setting /Network/Router/QoS properties')
        QoSOrg.setZenProperty( 'zCollectorPlugins', plugins )
        self.rebuildRelations(app.zport.dmd)
        log.info('Install pysnmp')
        os.system('easy_install pysnmp')


    def remove(self, app, leaveObjects=False):
        if not leaveObjects:
            self.removePluginSymlink()
            log.info('Removing devices')
            for i in app.dmd.Devices.Network.Router.QoS.getSubDevices():
                i.deleteDevice()
            log.info('Removing QoS organizer')
            app.dmd.Devices.Network.Router.manage_deleteOrganizer('QoS')
        super(ZenPack, self).remove(app, leaveObjects=leaveObjects)
        self.rebuildRelations(app.zport.dmd)


    def symlinkPlugin(self):
        log.info('Nothing needing linking.')


    def removePluginSymlink(self):
        log.info('Nothing needing unlinking.')


    def rebuildRelations(self, dmd):
        log.info('Building device relations [This could take a long time]')
        # Build relations on all devices
        try:
            from transaction import commit
            for d in dmd.Devices.getSubDevices():
                d.os.buildRelations()
                commit()
        except Exception, e:
            log.error('Some unknown problem occured during relationship construction: %s' % (e))
            pass

            log.info("Done rebuild relations")

