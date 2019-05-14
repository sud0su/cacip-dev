# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2012 OpenPlans
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

# DASHBOARD_TO_APP = {
# 	'floodforecast': 'flood',
# 	'floodrisk': 'flood',
# 	'avalancherisk': 'avalanche',
# 	'avalcheforecast': 'avalanche', # inherited misspelling
# 	'avalancheforecast': 'avalanche',
# 	'accessibility': 'accessibility',
# 	'earthquake': 'earthquake',
# 	'security': 'securityincident',
# 	'landslide': 'landslide',
# 	'drought': 'drought',
# 	'naturaldisaster': 'naturaldisaster',
# 	'weather': 'weather',
# 	'drought': 'drought',
# }

# EPR-BGD
def build_dashboard_meta():
	print 'def build_dashboard_meta() start'

	from geonode.settings import INSTALLED_APPS, STATICFILES_DIRS

	from django.utils.translation import ugettext as _
	from geonode.utils import dict_ext

	import django
	import importlib
	import json
	import os

    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geonode.settings")
	# if __name__ == '__main__':
	# 	django.setup()

	# build dashboard menu data and 
	# dashboard page to app name mapping
	dashboard_to_app = {}
	dashboard_apps = []
	# menus = [{'title':_('Quick Overview'),'name':'main'},{'title':_('Baseline'),'name':'baseline'}]
	menus = []
	# print 'INSTALLED_APPS', INSTALLED_APPS
	for modname in [app for app in INSTALLED_APPS if app.startswith('dashboard.')]:
		# print 'modname', modname
		module = importlib.import_module('%s.enumerations'%(modname))
		try:
			dashboard_meta = dict_ext(module.DASHBOARD_META)
			# print 'dashboard_meta', dashboard_meta
		except Exception as e:
			continue
		else:
			try:
				dashboard_apps += [modname]
				menuitem = {
					'title':_(dashboard_meta.get('menutitle','')),
					'name':dashboard_meta.get('name',''),
					'child':[]
				}
				for v in dashboard_meta.get('pages',[]):
					menuitem['child'].append({
						'title':_(v['menutitle']),
						'name':v['name']
					})
					dashboard_to_app[v['name']] = modname
				menuitem = menuitem['child'][0] if len(menuitem['child']) == 1 else menuitem
				menus.append(menuitem)
			except Exception as e:
				pass

	DASHBOARD_META = {
		'DASHBOARD_PAGE_MENU':menus,
		'DASHBOARD_TO_APP':dashboard_to_app,
		'DASHBOARD_APPS':dashboard_apps,
	}

	# with open(os.path.join(STATICFILES_DIRS[0],'dashboard_meta.json'), 'w') as f:
	# 	f.write(json.dumps(DASHBOARD_META))

	return DASHBOARD_META

DASHBOARD_META = build_dashboard_meta()
print 'DASHBOARD_META', DASHBOARD_META
