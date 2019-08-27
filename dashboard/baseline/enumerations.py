DASHBOARD_META = {
    'pages': [
        {
            'name': 'baseline',
            'function': 'get_baseline', 
            'template': 'dash_baseline.html',
            'menutitle': 'Baseline',
        },
    ],
    'menutitle': 'Baseline',
}

ADM_TYPES = {
    0: 'district',
    1: 'upazila',
    2: 'union',
    3: 'camp',
}

ADM_FIELDS = ['district', 'upazila', 'union', 'new_camp_n']

AGE_GROUP_TYPES = {
    'infant': '< 1',
    '1_4': '1 - 4',
    '5_11': '5 - 11',
    '12_17': '12 - 17',
    '18_59': '18 - 59',
    '60': '60 +',
}
AGE_GROUP_TYPES_KEYS = ['infant', '1_4', '5_11', '12_17', '18_59', '60']