import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","geonode.settings")
if __name__ == '__main__':
    import django
    django.setup()

from django.conf import settings
from geonode.base.models import Region# echo Remove obsolete entries
from geonode.documents.models import Document
from itertools import tee
from pprint import pprint
# from .views import uploadpdf
import argparse
import csv
# import geonode.documents.models
import glob
import logging
import sys
import traceback
import copy

parser = argparse.ArgumentParser(description='Process uploaded static map data and pdf.')
parser.add_argument('--csvin', default='uploadlist.csv', help='input csv file')
parser.add_argument('--csvout', default='uploadedlist.csv', help='output csv file')
parser.add_argument('--pdfpathin', default='/home/uploader/documents/', help='path to input pdf file')
parser.add_argument('--pdfpathout', default=os.path.expanduser(settings.MEDIA_ROOT), help='path to output pdf file')
parser.add_argument('--pdfsubpathout', default='documents/', help='sub path to output pdf file')
args = parser.parse_args()

# path_source = '/home/dodi/tmp/uploader/161213/'
# path_source = '/home/uploader/161213/'
# fin_up_path = '96_Geonode/'
# path_dest = '/home/dodi/tmp/uploaded/'+fin_up_path
# path_dest = '/home/ubuntu/DRR-datacenter/geonode/uploaded/'+fin_up_path
# u = uploadpdf() # instantiate class to init uploadpdf logging
logging.basicConfig()
logger = logging.getLogger(__name__)
current_folder = os.path.dirname(os.path.realpath(__file__))+'/'
logger.info('Script \'%s\' start.'%(os.path.basename(__file__)))

# log error traceback messages
def exception_hook(exc_type, exc_value, exc_traceback):
    logger.error(
        "Uncaught exception",
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    sys.exit('Uncaught exception')

sys.excepthook = exception_hook

# hardcoded to simplify
# fname_csv_in = sys.argv[1]
# fname_csv_out = sys.argv[2]
path_source = args.pdfpathin
fname_csv_in = args.csvin or os.path.join(args.pdfpathin,'uploadlist.csv')
fname_csv_out = args.csvout or os.path.join(args.pdfpathin,'uploadedlist.csv')
fin_up_path = args.pdfsubpathout 
path_dest = os.path.join(args.pdfpathout,args.pdfsubpathout)
# print 'path_dest', path_dest

f_IN = open(fname_csv_in, 'r+U')
f_OUT= open(fname_csv_out, 'wt')
first = True
try:
	reader = csv.reader(f_IN)
	writer = csv.writer(f_OUT)
	remaining = list(reader)
	f_IN.seek(0)
	for idx, row in enumerate(reader):
		# print 'idx', idx
		if not row:
			continue
		elif first:
			columns = copy.copy(row)
			# print 'columns', columns
			first = False
		else:

			# if (Document.objects.filter(doc_file__icontains=row[0])):
			# 	raise Exception('FileName \'%s\' already exist'%(row[0]))		

			# logger.debug(row)
			fullpath_source = os.path.normpath(os.path.join(path_source,row[10],row[0]))
			# print 'fullpath_source', fullpath_source
			if os.path.isfile(fullpath_source):
				print 'Processing %s'%(fullpath_source)
				kwargs = {
					'doc_file':os.path.normpath(os.path.join(args.pdfsubpathout,row[10],row[0])),
					'title':row[1],
					'owner_id':1000,
					'papersize':row[8],
					'datasource':row[2],
					'subtitle':row[12],
					'category_id':row[5],
					'date':row[9],
					'abstract':row[14],
				}
				# print 'kwargs', kwargs
				if (len(row) > 18) and (row[18]):
					# prev_file_name exist
					try:
						newdata = Document.objects.get(doc_file__icontains=row[18])
						# alternative to newdata.update(**kwargs)
						for (key, value) in kwargs.items():
							setattr(newdata, key, value)
					except Document.DoesNotExist:
						raise Exception('previous_file_name \'%s\' not found in database.'%(row[18]))
					except Document.MultipleObjectsReturned:
						raise Exception('previous_file_name \'%s\' returns multiple row.'%(row[18]))
				else:
					# no prev_file_name
					newdata = Document(**kwargs)

				fullpath_dest = os.path.normpath(os.path.join(path_dest,row[10],row[0]))
				# print 'fullpath_dest', fullpath_dest
			
				if not os.path.exists(os.path.dirname(fullpath_dest)):
					os.makedirs(os.path.dirname(fullpath_dest))
				
				os.rename(fullpath_source, fullpath_dest)
				newdata.save()
				valid_keywords = filter(None, row[7].split("-"))
				newdata.keywords.add(*valid_keywords)
				row[16] = newdata.id
				loc = Region.objects.get(pk=row[4])
				newdata.regions.add(loc)

				# delete row based on row[0]
				for delidx, delrow in enumerate(remaining):
					if delrow and (delrow[0] == row[0]):
						del remaining[delidx]
						break

				msg_success = 'Upload pdf succesfull: %s.'%(row[0])
				print msg_success
				logger.info(msg_success)
			else:
				raise Exception('File \'%s\' not found.'%(fullpath_source))
		writer.writerow(row)
	if first or (idx == 0):
		raise Exception('No rows data.')
except Exception as e:
	# print e.message
	logger.error(e.message+'\n'+traceback.format_exc())
	# sys.exit(e.message)
finally:

	# write remaining list back to f_IN
	f_IN.seek(0)
	csv.writer(f_IN).writerows(remaining)
	f_IN.truncate()

	f_IN.close()
	f_OUT.close()

	if 'e' in locals():
		emsg = e.message
		if 'row' in locals():
			emsg = "Error on row: {0}. {1}".format(row[0], emsg)
		sys.exit(emsg)
