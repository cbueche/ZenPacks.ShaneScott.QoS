import copy
import logging
log = logging.getLogger("zen.ZenQoS")

import locale

from Globals import DTMLFile
from Globals import InitializeClass
from Products.ZenModel.OSComponent import OSComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.ZenUtils.Utils import convToUnits, prepId
from Products.ZenRelations.RelSchema import *
from Products.ZenModel.ZenossSecurity import *
from AccessControl import ClassSecurityInfo

class ClassMap(OSComponent): 
    """QoS ClassMap Object"""

    ZENPACKID = 'ZenPacks.ShaneScott.QoS'

    portal_type = meta_type = 'ClassMap'

    instance = ''
    allocName = ''
    parentInterface = ''
    parentServicePolicy = ''
    unifiedLegend = ''
    direction = ''
    allocBandwidth = ''
    policeRate = ''
    allocType = ''

    _properties = OSComponent._properties + (
        {'id':'instance', 'type':'string', 'mode':'w'},
        {'id':'allocName', 'type':'string', 'mode':'w'},
        {'id':'parentInterface', 'type':'string', 'mode':'w'},
        {'id':'parentServicePolicy', 'type':'string', 'mode':'w'},
        {'id':'unifiedLegend', 'type':'string', 'mode':'w'},
        {'id':'direction', 'type':'string', 'mode':'w'},
        {'id':'allocBandwidth', 'type':'string', 'mode':'w'},
        {'id':'policeRate', 'type':'string', 'mode':'w'},
        {'id':'allocType', 'type':'string', 'mode':'w'},
        )

    _relations = OSComponent._relations + (
        ("os", ToOne(ToManyCont, "Products.ZenModel.OperatingSystem", "classes")),
        )

    ClassMapTypeMap = ('Parent','Child')

    factory_type_information = (
        {
            'id'         : 'ClassMap',
            'meta_type'      : 'ClassMap',
            'description'    : """QoS ClassMap Object""",
            'icon'       : 'Device_icon.gif',
            'product'    : 'ClassMap',
            'factory'    : 'manage_addClassMap',
            'immediate_view' : 'ClassMapPerformance',
            'actions'    : ''
        },
    )


    security = ClassSecurityInfo()

    def __init__(self, id, title = None):
        """
        Init OSComponent
        """
        OSComponent.__init__(self, id, title)
        self.buildRelations()


    def deviceId(self):
        """
        The device id, for indexing purposes.
        """
        d = self.device()
        if d: return d.getPrimaryId()
        else: return None

    def getId(self):
        return self.id

    def getInstance(self):
        return self.instance

    def getAllocName(self):
        return self.allocName

    def getParentInterface(self):
        return self.parentInterface

    def getDirection(self):
        return self.direction

    def getParentServicePolicy(self):
        return self.parentServicePolicy

    def getUnifiedLegend(self):
        return self.unifiedLegend

    def getAllocBandwidth(self):
        return self.allocBandwidth

    def getAllocBandwidthNsuffix(self):
        allocBandwidth = self.allocBandwidth + ' ' + str(self.allocType)
        if allocBandwidth == '0 kbps':
            allocBandwidth = ''
        return allocBandwidth

    def getPoliceRate(self):
        return self.policeRate

    def viewName(self):
        return self.id
    name = primarySortKey = viewName


    def managedDeviceLink(self):
        from Products.ZenModel.ZenModelRM import ZenModelRM
        d = self.getDmdRoot("Devices").findDevice(self.id)
        if d:
            return ZenModelRM.urlLink(d, 'link')
        return None

    def manage_editProperties(self, REQUEST):
        """
        Override from propertiyManager so we can trap errors
        """
        return ConfmonPropManager.manage_editProperties(self, REQUEST)


    def getRRDTemplateName(self):
        """
        Return the interface type as the target type name.
        """
        return "QoS_ClassMap"

    def getRRDTemplates(self):
        """
        Return a list containing the appropriate RRDTemplate for this ClassMap.
        """
        templateName = self.getRRDTemplateName()
        default = self.getRRDTemplateByName(templateName)

        if not default:
            default = self.getRRDTemplateByName("QoS_ClassMap")

        if default:
            return [default]
        return []

InitializeClass(ClassMap)
