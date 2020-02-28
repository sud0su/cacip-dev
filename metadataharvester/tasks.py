from celery.app import shared_task, task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task(bind=True, queue='harvester')
def test(self):
    print('Hello', self)

@shared_task(bind=True, queue='harvester')
def update_documents_okrworldbank_oai(self):
    from metadataharvester.api import documents_okrworldbank_oai
    harvester = documents_okrworldbank_oai.Harvester()
    harvester.harvest_latest()
    harvester.create_all_thumbnail()

@shared_task(bind=True, queue='harvester')
def update_documents_projects_ctcn(self):
    from metadataharvester.api import documents_projects_ctcn
    harvester = documents_projects_ctcn.Harvester()
    harvester.harvest_latest()

@shared_task(bind=True, queue='harvester')
def update_documents_resourcedataorg_ckan(self):
    from metadataharvester.api import documents_resourcedataorg_ckan
    harvester = documents_resourcedataorg_ckan.Harvester()
    harvester.harvest_latest()

@shared_task(bind=True, queue='harvester')
def update_documents_webinar_ctcn(self):
    from metadataharvester.api import documents_webinar_ctcn
    harvester = documents_webinar_ctcn.Harvester()
    harvester.harvest_latest()

@shared_task(bind=True, queue='harvester')
def update_events_ctcn(self):
    from metadataharvester.api import events_ctcn
    harvester = events_ctcn.Harvester()
    harvester.harvest_latest()

@shared_task(bind=True, queue='harvester')
def update_news_ctcn(self):
    from metadataharvester.api import news_ctcn
    harvester = news_ctcn.Harvester()
    harvester.harvest_latest()

@shared_task(bind=True, queue='harvester')
def update_news_caiag_kg_rss(self):
    from metadataharvester.rss import news_caiag_kg_rss
    harvester = news_caiag_kg_rss.Harvester()
    harvester.harvest_latest()

@shared_task(bind=True, queue='harvester')
def update_news_infoclimate_rss(self):
    from metadataharvester.rss import news_infoclimate_rss
    harvester = news_infoclimate_rss.Harvester()
    harvester.harvest_latest()

@shared_task(bind=True, queue='harvester')
def update_news_infoik_rss(self):
    from metadataharvester.rss import news_infoik_rss
    harvester = news_infoik_rss.Harvester()
    harvester.harvest_latest()

@shared_task(bind=True, queue='harvester')
def update_news_med_rss(self):
    from metadataharvester.rss import news_med_rss
    harvester = news_med_rss.Harvester()
    harvester.harvest_latest()

@shared_task(bind=True, queue='harvester')
def update_news_statkg_rss(self):
    from metadataharvester.rss import news_statkg_rss
    harvester = news_statkg_rss.Harvester()
    harvester.harvest_latest()
