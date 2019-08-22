DASHBOARD_META = {
    'pages': [
        {
            'name': 'reporthub',
            'function': 'get_reporthub',
            'template': 'dash_healthsector.html',
            'menutitle': 'ReportHub',
        },
        # {
        #     'name': 'protectionsector',
        #     'function': 'get_protectionsector',
        #     'template': 'dash_protectionsector.html',
        #     'menutitle': 'Protection Sector',
        # },
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
