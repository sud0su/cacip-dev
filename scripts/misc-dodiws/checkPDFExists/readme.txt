# change user to uploader
su uploader
cd ~
mkdir documents

# ftp upload pdf files, uploadlist.csv, uploadedlist.csv to /home/uploader/documents/

# add all file read-write permission for all user in folder documents
sudo chmod a+rw documents -R

# change to default user 'ubuntu'
su ubuntu
# go to project root
cd ~/EPR-BGD01/EPR-BGD01
# run script
python scripts/misc-dodiws/checkPDFExists/checkPDFExists.py \
--csvin /home/uploader/documents/uploadlist.csv \
--csvout /home/uploader/documents/uploadedlist.csv \
--pdfpathin /home/uploader/documents/ 