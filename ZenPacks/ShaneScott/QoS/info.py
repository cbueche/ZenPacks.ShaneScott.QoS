from zope.component import adapts
from zope.interface import implements

from Products.ZenUtils.Utils import convToUnits

from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.component import ComponentInfo
from Products.Zuul.infos.template import RRDDataSourceInfo

from ZenPacks.ShaneScott.QoS.ServicePolicy import ServicePolicy
from ZenPacks.ShaneScott.QoS.Policy import Policy
from ZenPacks.ShaneScott.QoS.ClassMap import ClassMap

from ZenPacks.ShaneScott.QoS.interfaces import IPolicyInfo, IClassMapInfo, IServicePolicyInfo

class ServicePolicyInfo(ComponentInfo):
    implements(IServicePolicyInfo)
    adapts(ServicePolicy)

    instance = ProxyProperty("instance")
    parentInterface = ProxyProperty("parentInterface")
    direction = ProxyProperty("direction")
    allocName = ProxyProperty("allocName")

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
    def allocName(self):
        return self._object.getAllocName()

class ClassMapInfo(ComponentInfo):
    implements(IClassMapInfo)
    adapts(ClassMap)

    instance = ProxyProperty("instance")
    parentInterface = ProxyProperty("parentInterface")
    parentServicePolicy = ProxyProperty("parentServicePolicy")
    direction = ProxyProperty("direction")
    allocBandwidth = ProxyProperty("allocBandwidth")
    allocName = ProxyProperty("allocName")

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
    def allocBandwidth(self):
        return self._object.getAllocBandwidth()

    @property
    def allocBandwidthNsuffix(self):
        return self._object.getAllocBandwidthNsuffix()

    @property
    def allocName(self):
        return self._object.getAllocName()

class PolicyInfo(ComponentInfo):
    implements(IPolicyInfo)
    adapts(Policy)

    instance = ProxyProperty("instance")
    parentInterface = ProxyProperty("parentInterface")
    parentClassMap = ProxyProperty("parentClassMap")
    parentServicePolicy = ProxyProperty("parentServicePolicy")
    direction = ProxyProperty("direction")
    allocName = ProxyProperty("allocName")

    @property
    def instance(self):
        return self._object.getInstance()

    @property
    def parentInterface(self):
        return self._object.getParentInterface()

    @property
    def parentClassMap(self):
        return self._object.getParentClassMap()

    @property
    def parentServicePolicy(self):
        return self._object.getParentServicePolicy()

    @property
    def direction(self):
        return self._object.getDirection()

    @property
    def allocName(self):
        return self._object.getAllocName()

    @property
    def allocNameNsuffix(self):
        return self._object.getAllocNameNsuffix()
