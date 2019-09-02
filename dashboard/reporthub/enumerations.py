DASHBOARD_META = {
    'pages': [
        {
            'name': 'healthsector',
            'id': 'health',
            'function': 'get_reporthub',
            'template': 'dash_healthsector.html',
            'menutitle': 'Health Sector',
            'cluster_id': 'health',
        },
        {
            'name': 'protectionsector',
            'id': 'protection',
            'function': 'get_reporthub',
            'template': 'dash_protectionsector.html',
            'menutitle': 'Protection Sector',
            'cluster_id': 'protection',
        },
        {
            'name': 'foodsecuritysector',
            'id': 'fss',
            'function': 'get_reporthub',
            'template': 'dash_foodsecuritysector.html',
            'menutitle': 'Food Security Sector',
            'cluster_id': 'fss',
        },
        {
            'name': 'nutritionsector',
            'id': 'nutrition',
            'function': 'get_reporthub',
            'template': 'dash_nutritionsector.html',
            'menutitle': 'Nutrition Sector',
            'cluster_id': 'nutrition',
        },
        {
            'name': 'washsector',
            'id': 'wash',
            'function': 'get_reporthub',
            'template': 'dash_washsector.html',
            'menutitle': 'WASH Sector',
            'cluster_id': 'wash',
        },
        {
            'name': 'smsdsector',
            'id': 'smsd',
            'function': 'get_reporthub',
            'template': 'dash_smsdsector.html',
            'menutitle': 'Site Management, Site Development and DRR Sector',
            'cluster_id': 'smsd',
        },
    ],
    'menutitle': 'ReportHub',
}

ADM_TYPES = {
    0: 'district',
    1: 'upazila',
    2: 'union',
    3: 'camp',
    4: 'subcamp',
}

ADM_NAME_FIELDS = {
    'admin0pcode': 'admin0name', 
    'admin1pcode': 'admin1name', 
    'admin2pcode': 'admin2name', 
    'admin3pcode': 'admin3name', 
    'admin4pcode': 'admin4name',
}
ADM_CODE_FIELDS = ['admin0pcode', 'admin1pcode', 'admin2pcode', 'admin3pcode', 'admin4pcode']

FILTER_NAME_FIELDS = {
    'cluster_id': 'cluster', 
    'organization': 'organization', 
    'activity_description_id': 'activity_description_name', 
}
FILTER_CODE_FIELDS = ['cluster_id', 'organization', 'activity_description_id']

FILTER_OPTIONAL_FIELDS = ['donor','organization','reporting_period','unit_type_id']
FILTER_OPTIONAL_FIELDS_NAME = {
    'donor': 'donor',
    'organization': 'organization',
    'cluster_id': 'cluster',
    'reporting_period': 'reporting_period',
    'unit_type_id': 'unit_type_name',
}
