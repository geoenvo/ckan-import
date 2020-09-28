#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import pprint
import re
import argparse

import requests


#DATASET_DIRS = ['/path/to/datasets1', '/path/to/datasets2']
#DATASET_DIRS = ['D:\path\to\datasets1', 'D:\path\to\datasets2']
DEFAULT_EXTS_UPLOAD = [
    '.docx',
    '.xlsx',
    '.pptx',
    '.doc',
    '.xls',
    '.ppt',
    '.odt',
    '.ods',
    '.odp',
    '.pdf',
    '.csv',
    '.zip'
]
VALID_PRIVATE = ['True', 'False']
DEFAULT_PRIVATE = 'True'


def get_dataset_name(dataset_title):
    """Convert the dataset title to name with max length 100 chars and only lowercase alpanumeric, -, and _.
    
    Args:
      dataset_title: full dataset title string
    """
    dataset_name = dataset_title[0:100]
    dataset_name = dataset_title.strip()
    dataset_name = dataset_title.lower()
    dataset_name = dataset_name.replace(' ', '-')
    regex = re.compile(r'[^a-zA-Z0-9\-\_]')
    dataset_name = regex.sub('', dataset_name)
    return dataset_name

def ckan_create_dataset(ckan_base_url, ckan_api_key, dataset_name, dataset_title, dataset_private, dataset_owner_org, resource_filepath, resource_filename):
    """Perform the requests to the CKAN API for creating a new dataset and uploading a resource file.
    
    Args:
      ckan_base_url: the URL to the CKAN site
      ckan_api_key: the CKAN API key
      dataset_name: unique 100 char max lowercase alpanumeric string in CKAN
      dataset_title: the full title of the dataset
      dataset_private: True or False
      dataset_owner_org: the dataset owner organization
      resource_filepath: the full path to the resource file
      resource_filename: the filename of the resource file (with extension)
    """
    headers = {'Authorization': ckan_api_key}
    dataset_data = {
        'name': dataset_name,
        'title': dataset_title,
        #'description': dataset_title,
        'private': dataset_private,
        'owner_org': dataset_owner_org
    }
    # make the HTTP request
    # create the dataset first...
    response = requests.post(ckan_base_url + 'api/3/action/package_create', headers=headers, data=dataset_data)
    #assert response.status_code == requests.codes.ok
    if response.status_code == requests.codes.ok:
        # if return status_code 200 then the dataset is created successfully
        # Use the json module to load CKAN's response into a dictionary.
        response_dict = json.loads(response.content)

        # Check the contents of the response.
        assert response_dict['success'] is True
        result = response_dict['result']
        #pprint.pprint(result)
        
        # after the dataset is created, now create the resource for the dataset
        resource_data = {
            'package_id': dataset_data['name'],
            'name': resource_filename,
            #'description': 'resource description',
            #'format': ''
        }
        resource_file = {
            'upload': open(resource_filepath, 'rb')
        }
        with open(resource_filepath, 'rb') as f:
            resource_file = {
                'upload': f
            }
            response = requests.post(ckan_base_url + 'api/3/action/resource_create', headers=headers, data=resource_data, files=resource_file)
        #assert response.status_code == requests.codes.ok
        if response.status_code == requests.codes.ok:
            response_dict = json.loads(response.content)

            # Check the contents of the response.
            assert response_dict['success'] is True
            result = response_dict['result']
            #pprint.pprint(result)
            return True, None
        else:
            # failed to create the resource
            return_message = json.loads(response.content)
            error_message = return_message['error']['name'][0]
            return False, error_message
    else:
        return_message = json.loads(response.content)
        error_message = None
        # error: api key not authorized
        try:
            error_message = return_message['error']['message']
        except:
            pass
        # error: owner org does not exist
        try:
            error_message = return_message['error']['owner_org'][0]
        except:
            pass
        # error: status_code 409 = duplicate dataset name (url)
        try:
            error_message = return_message['error']['name'][0]
        except:
            pass
        return False, error_message


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Import dataset files to CKAN',
        epilog='Refer to https://github.com/geoenvo/ckan-import for more details')
    parser.add_argument('-c', '--ckan-base-url', help='The URL of the CKAN site (example: http://myckan.site/)', type=str, required=True)
    parser.add_argument('-a', '--ckan-api-key', help='The CKAN API key (must have the permission to create datasets)', type=str, required=True)
    parser.add_argument('-d', '--dirs', help='Directory path(s) containing dataset files to import', type=str, nargs='+', required=True)
    parser.add_argument('-e', '--exts-upload', help='File extensions to upload (defaults to: {})'.format(' '.join(DEFAULT_EXTS_UPLOAD)), type=str, nargs='+', default=DEFAULT_EXTS_UPLOAD)
    parser.add_argument('-p', '--private', help='Set the visibility of the datasets to private (True or False, defaults to: {})'.format(DEFAULT_PRIVATE), type=str, default=DEFAULT_PRIVATE)
    parser.add_argument('-o', '--owner-org', help='The owner organization of the datasets', type=str, required=True)
    args = parser.parse_args()
    ckan_base_url = args.ckan_base_url
    ckan_api_key = args.ckan_api_key
    dataset_dirs = args.dirs
    exts_upload = args.exts_upload
    dataset_private = args.private
    dataset_owner_org = args.owner_org
    #print(ckan_base_url)
    #print(ckan_api_key)
    #print(dataset_dirs)
    #print(exts_upload)
    #print(dataset_private)
    #print(dataset_owner_org)
    # check parameters first
    if not ckan_base_url.endswith('/'):
        ckan_base_url = '{}/'.format(ckan_base_url)
    for check_dataset_dir in dataset_dirs:
        if not os.path.isdir(check_dataset_dir):
            print('ERROR: invalid dataset directory path (got {})'.format(check_dataset_dir))
            sys.exit()
    if dataset_private not in VALID_PRIVATE:
        print('ERROR: private must be True or False (got {})'.format(dataset_private))
        sys.exit()
    #sys.exit(0)
    count_dataset_dirs = 0
    count_dataset_total = 0
    count_dataset_import_successful = 0
    count_dataset_import_failed = 0
    for dataset_dir in dataset_dirs:
        print('Processing dataset directory: {}'.format(dataset_dir))
        for root, dirs, files in os.walk(dataset_dir):
            for filename in files:
                for ext in exts_upload:
                    if filename.lower().endswith(ext):
                        filepath = os.path.join(root, filename)
                        #print(filepath, filename)
                        # get the dataset title from the filename without the extension part
                        dataset_title = filename.split('.')[0]
                        # dataset name max length is 100 chars only allows lowercase alpanumeric, -, and _
                        dataset_name = get_dataset_name(dataset_title)
                        dataset_created, error_message = ckan_create_dataset(ckan_base_url, ckan_api_key, dataset_name, dataset_title, dataset_private, dataset_owner_org, filepath, filename)
                        if dataset_created:
                            print('SUCCESS: imported dataset "{}"'.format(dataset_title))
                            count_dataset_import_successful += 1
                        else:
                            print('FAILED: cannot import dataset "{}" (got error message "{}")'.format(dataset_title, error_message))
                            count_dataset_import_failed += 1
                        count_dataset_total += 1
        count_dataset_dirs += 1
    print('SUMMARY')
    print('Dataset directories processed\t: {}'.format(count_dataset_dirs))
    print('Dataset imported\t\t: {}'.format(count_dataset_import_successful))
    print('Dataset import failed\t\t: {}'.format(count_dataset_import_failed))
    print('Dataset total\t\t\t: {}'.format(count_dataset_total))
    sys.exit(0)
