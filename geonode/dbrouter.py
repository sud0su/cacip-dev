'''
settings.MAP_APPS_TO_DB is a dict to map app to db
any app not in settings.MAP_APPS_TO_DB will return None (no opinion)
'''

from django.conf import settings

# DB_LIST = set(settings.MAP_APPS_TO_DB.values())

class defaultdbrouter(object):

    def db_for_read(self, model, **hints):

        # if model._meta.app_label in settings.MAP_APPS_TO_DB:
        #     return settings.MAP_APPS_TO_DB[model._meta.app_label]
        # return DEFAULTDB
        return settings.MAP_APPS_TO_DB.get(model._meta.app_label)

    def db_for_write(self, model, **hints):

        # if model._meta.app_label in settings.MAP_APPS_TO_DB:
        #     return settings.MAP_APPS_TO_DB[model._meta.app_label]
        # return DEFAULTDB
        return settings.MAP_APPS_TO_DB.get(model._meta.app_label)

    def allow_relation(self, obj1, obj2, **hints):

        db1 = settings.MAP_APPS_TO_DB.get(obj1._meta.app_label)
        db2 = settings.MAP_APPS_TO_DB.get(obj2._meta.app_label)
        if db1 and db2:
            return db1 == db2
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        # if db in settings.MAP_APPS_TO_DB.values():
        #     return settings.MAP_APPS_TO_DB.get(app_label) == db
        # elif app_label in settings.MAP_APPS_TO_DB:
        #     return False
        # return None
        # print 'db', db
        # print 'app_label', app_label
        # print 'model_name', model_name
        # print 'hints', hints
        # if db in DB_LIST:
        #     return settings.MAP_APPS_TO_DB.get(app_label) == db
        # else:
        #     return None
        db_mapped = settings.MAP_APPS_TO_DB.get(app_label)
        if db_mapped:
            return db_mapped == db
        else:
            return None
        
