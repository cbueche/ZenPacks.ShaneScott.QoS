from Products.Zuul.interfaces import IInfo, IComponentInfo
from Products.Zuul.form import schema
from Products.Zuul.interfaces import IFacade
from Products.Zuul.interfaces import IDeviceInfo
from Products.Zuul.utils import ZuulMessageFactory as _t
from Products.ZenModel.ZVersion import VERSION as ZENOSS_VERSION
from Products.ZenUtils.Version import Version

if Version.parse('Zenoss %s' % ZENOSS_VERSION) >= Version.parse('Zenoss 4'):
    SingleLineText = schema.TextLine
    MultiLineText = schema.Text
else:
    SingleLineText = schema.Text
    MultiLineText = schema.TextLine

class IClassMapInfo(IComponentInfo):
    """
    Info adapter for ClassMap components.
    """
    instance = schema.Text(title=_t(u"Instance"), readonly=True, group='Overview')
    parentInterface = schema.Text(title=_t(u"Interface"), readonly=True, group='Overview')
    direction = schema.Text(title=_t(u"Direction"), readonly=True, group='Overview')
    allocBandwidth = schema.Text(title=_t(u"Bandwidth"), readonly=True, group='Overview')
    parentServicePolicy = schema.Text(title=_t(u"Policy"), readonly=True, group='Overview')
    unifiedLegend = schema.Text(title=_t(u"Legend"), readonly=True, group='Overview')
    policeRate = schema.Text(title=_t(u"PoliceRate"), readonly=True, group='Overview')
