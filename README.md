# ckan-import.py


## How to run
This script will import dataset files from a directory for a CKAN organization.

Example below: import the private dataset files from the directory `d:\datasets` for the organization `orgname` at CKAN site `http://www.myckan.site/`
````
# ckan-import.py requires the Requests library
pip install requirements.txt

python ckan-import -h
usage: ckan-import.py [-h] -c CKAN_BASE_URL -a CKAN_API_KEY -d DIRS [DIRS ...]
                      [-e EXTS_UPLOAD [EXTS_UPLOAD ...]] [-p PRIVATE] -o
                      OWNER_ORG

Import dataset files to CKAN

optional arguments:
  -h, --help            show this help message and exit
  -c CKAN_BASE_URL, --ckan-base-url CKAN_BASE_URL
                        The URL of the CKAN site (example:
                        http://www.myckan.site/)
  -a CKAN_API_KEY, --ckan-api-key CKAN_API_KEY
                        The CKAN API key (must have the permission to create
                        datasets)
  -d DIRS [DIRS ...], --dirs DIRS [DIRS ...]
                        Directory path(s) containing dataset files to import
  -e EXTS_UPLOAD [EXTS_UPLOAD ...], --exts-upload EXTS_UPLOAD [EXTS_UPLOAD ...]
                        File extensions to upload (defaults to: .docx .xlsx
                        .pptx .pdf .csv .zip)
  -p PRIVATE, --private PRIVATE
                        Set the visibility of the datasets to private (True or
                        False, defaults to: True)
  -o OWNER_ORG, --owner-org OWNER_ORG
                        The owner organization of the datasets

Refer to https://github.com/geoenvo/ckan-import for more details

python ckan-import.py -c http://www.myckan.site/ -a xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx -d d:\datasets -p True -o orgname
````
