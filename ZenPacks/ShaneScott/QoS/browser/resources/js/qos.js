(function(){

var ZC = Ext.ns('Zenoss.component');

function render_link(ob) {
    if (ob && ob.uid) {
        return Zenoss.render.link(ob.uid);
    } else {
        return ob;
    }
}

ZC.ServicePolicyPanel = Ext.extend(ZC.ComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'name',
            componentType: 'ServicePolicy',
            sortInfo: {
                field: 'allocName',
                direction: 'ASC'
            },
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'allocName'},
                {name: 'parentInterface'},
                {name: 'direction'},
                {name: 'hasMonitor'},
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'},
            ],
            columns: [{
                id: 'name',
                dataIndex: 'allocName',
                header: _t('Service Policy'),
                width: 70,
                sortable: true
            },{
                id: 'parentInterface',
                dataIndex: 'parentInterface',
                header: _t('Interface'),
                width: 120,
                sortable: true
            },{
                id: 'direction',
                dataIndex: 'direction',
                header: _t('Direction'),
                width: 70,
                sortable: true
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                width: 70,
                sortable: true
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                width: 72,
                renderer: Zenoss.render.locking_icons
            }]
        });
        ZC.ServicePolicyPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('ServicePolicyPanel', ZC.ServicePolicyPanel);
ZC.registerName('ServicePolicy', _t('Service Policy'), _t('Service Policies'));

ZC.ClassMapPanel = Ext.extend(ZC.ComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'name',
            componentType: 'ClassMap',
            sortInfo: {
                field: 'name',
                direction: 'ASC'
            },
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'allocName'},
                {name: 'parentInterface'},
                {name: 'parentServicePolicy'},
                {name: 'allocBandwidthNsuffix'},
                {name: 'direction'},
                {name: 'hasMonitor'},
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'},
            ],
            columns: [{
                id: 'name',
                dataIndex: 'name',
                header: _t('Full Name'),
                width: 70,
                sortable: true
            },{
                id: 'allocName',
                dataIndex: 'allocName',
                header: _t('Class Map'),
                width: 120,
                sortable: true
            },{
                id: 'parentServicePolicy',
                dataIndex: 'parentServicePolicy',
                header: _t('Service Policy'),
                width: 120,
                sortable: true
            },{
                id: 'parentInterface',
                dataIndex: 'parentInterface',
                header: _t('Interface'),
                width: 120,
                sortable: true
            },{
                id: 'direction',
                dataIndex: 'direction',
                header: _t('Direction'),
                width: 70,
                sortable: true
            },{
                id: 'allocBandwidthNsuffix',
                dataIndex: 'allocBandwidthNsuffix',
                header: _t('Bandwidth'),
                width: 70,
                sortable: true
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                width: 70,
                sortable: true
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                width: 72,
                renderer: Zenoss.render.locking_icons
            }]
        });
        ZC.ClassMapPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('ClassMapPanel', ZC.ClassMapPanel);
ZC.registerName('ClassMap', _t('Class Map'), _t('Class Maps'));

ZC.PolicyPanel = Ext.extend(ZC.ComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'name',
            componentType: 'Policy',
            sortInfo: {
                field: 'allocNameNsuffix',
                direction: 'ASC'
            },
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'allocNameNsuffix'},
                {name: 'parentClassMap'},
                {name: 'parentServicePolicy'},
                {name: 'parentInterface'},
                {name: 'direction'},
                {name: 'hasMonitor'},
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'},
            ],
            columns: [{
                id: 'parentClassMap',
                dataIndex: 'parentClassMap',
                header: _t('Class Map'),
                width: 120,
                sortable: true
            },{
                id: 'name',
                dataIndex: 'allocNameNsuffix',
                header: _t('Rate'),
                width: 70,
                sortable: true
            },{
                id: 'parentServicePolicy',
                dataIndex: 'parentServicePolicy',
                header: _t('Service Policy'),
                width: 120,
                sortable: true
            },{
                id: 'parentInterface',
                dataIndex: 'parentInterface',
                header: _t('Interface'),
                width: 120,
                sortable: true
            },{
                id: 'direction',
                dataIndex: 'direction',
                header: _t('Direction'),
                width: 70,
                sortable: true
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                width: 70,
                sortable: true
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                width: 72,
                renderer: Zenoss.render.locking_icons
            }]
        });
        ZC.PolicyPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('PolicyPanel', ZC.PolicyPanel);
ZC.registerName('Policy', _t('Policy'), _t('Policy'));

})();
