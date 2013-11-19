from zope.component import adapts
from zope.interface import implements

from Products.ZenUtils.Utils import convToUnits

from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.component import ComponentInfo
from Products.Zuul.infos.template import RRDDataSourceInfo

from ZenPacks.ShaneScott.QoS.ClassMap import ClassMap

from ZenPacks.ShaneScott.QoS.interfaces import IClassMapInfo

class ClassMapInfo(ComponentInfo):
    implements(IClassMapInfo)
    adapts(ClassMap)

    instance = ProxyProperty("instance")
    parentInterface = ProxyProperty("parentInterface")
    parentServicePolicy = ProxyProperty("parentServicePolicy")
    unifiedLegend = ProxyProperty("unifiedLegend")
    direction = ProxyProperty("direction")
    allocBandwidth = ProxyProperty("allocBandwidth")
    allocName = ProxyProperty("allocName")
    policeRate = ProxyProperty("policeRate")

    @property
    def instance(self):
        return self._object.getInstance()

    @property
    def parentInterface(self):
        return self._object.getParentInterface()

    @property
    def direction(self):
        return self._object.getDirection()

    @property
    def parentServicePolicy(self):
        return self._object.getParentServicePolicy()

    @property
    def unifiedLegend(self):
        return self._object.getUnifiedLegend()

    @property
    def policeRate(self):
        return self._object.getPoliceRate()

    @property
    def allocBandwidth(self):
        return self._object.getAllocBandwidth()

    @property
    def allocBandwidthNsuffix(self):
        return self._object.getAllocBandwidthNsuffix()

    @property
    def allocName(self):
        return self._object.getAllocName()
