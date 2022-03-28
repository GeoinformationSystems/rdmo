# RDMO to Ckan Plugin
# written by: Tim Taugnitz,  Professur für Geoinformatik, TU Dresden, https://tu-dresden.de/bu/umwelt/geo/geoinformatik
# The plugin links a metadata catalogue (here: a CKAN) with the RDMO software to enable researchers to manage dataset 
# metadata and DMP in a single tool. That facilitates researchers in managing metadata and DMP more efficient. When 
# entering dataset metadata in a DMP via RDMO, the developed plugin copies relevant metadata and publish the metadata 
# in the catalogue via catalogue API. We therefore modified a Science Europe template to fit to our developed metadata 
# profile for geodata. 


import zipfile
from collections import defaultdict

from django.http import HttpResponse
from rdmo.core.exports import prettify_xml
from rdmo.core.renderers import BaseXMLRenderer
from rdmo.projects.exports import Export


class Ckan(Export):

    scheme_uri = {
        'INSI': 'http://www.isni.org/',
        'ORCID': 'https://orcid.org',
        'ROR': 'https://ror.org/',
        'GRID': 'https://www.grid.ac/'
    }

    identifier_type_options = {
        # '': 'DOI',
        # '': 'OTHER'
    }

    language_options = {
        # '': 'en-US',
        # '': 'de-de'
    }

    name_type_options = {
        # '': 'Personal',
        # '': 'Organizational'
    }

    name_identifier_scheme_options = {
        # '': 'ORCID',
        # '': 'INSI',
        # '': 'ROR',
        # '': 'GRID'
    }

    contributor_type_options = {
        # '': 'ContactPerson',
        # '': 'DataCollector',
        # '': 'DataCurator',
        # '': 'DataManager',
        # '': 'Distributor',
        # '': 'Editor',
        # '': 'HostingInstitution',
        # '': 'Producer',
        # '': 'ProjectLeader',
        # '': 'ProjectManager',
        # '': 'ProjectMember',
        # '': '19RegistrationAgency',
        # '': 'RegistrationAuthority',
        # '': 'RelatedPerson',
        # '': 'Researcher',
        # '': 'ResearchGroup',
        # '': 'RightsHolder',
        # '': 'Sponsor',
        # '': 'Supervisor',
        # '': 'WorkPackageLeader',
        # '': 'Other'
    }

    resource_type_general_options = {
        # '': 'Audiovisual',
        # '': 'Collection',
        # '': 'DataPaper',
        # '': 'Dataset',
        # '': 'Event',
        # '': 'Image',
        # '': 'InteractiveResource',
        # '': 'Model',
        # '': 'PhysicalObject',
        # '': 'Service',
        # '': 'Software',
        # '': 'Sound',
        # '': 'Text',
        # '': 'Workflow',
        # '': 'Other'
    }

    rights_uri_options = {
        'dataset_license_types/71': 'https://creativecommons.org/licenses/by/4.0/',
        'dataset_license_types/73': 'https://creativecommons.org/licenses/by-nc/4.0/',
        'dataset_license_types/74': 'https://creativecommons.org/licenses/by-nd/4.0/',
        'dataset_license_types/75': 'https://creativecommons.org/licenses/by-sa/4.0/',
        'dataset_license_types/cc0': 'https://creativecommons.org/publicdomain/zero/1.0/deed.de'
    }


    def render(self):

        import requests
        import json
        from pprint import pprint
        import xml.dom.minidom

        # GET request
        request = 'add-server-ip/api/action/package_list'
        response = requests.post(request)
        titles_ckan = json.loads(response.content.decode())['result']

        # Required general information for the API-Request (later perhaps given by the questionnaire)
        API_TOKEN = '***'
        request = 'add-server-ip/api/action/package_create'

        # API-POST-Request
        # create dictionary with the needed information
        for dataset in self.get_datasets():
            titles = dataset.get('titles')
            dataset_dict = {
                'name': str(titles[0]['title'][:]).lower(),
                'contact_name': str(dataset.get('contactPoint')),
                'theme': dataset.get('theme'),
                'spatial': str(dataset.get('spatial')),
                'owner_org': 'rue_orga',
                'notes': dataset.get('description'),
                'conforms_to': dataset.get('conformsTo')
            }
            headers_dict = {
                'X-CKAN-API-Key': API_TOKEN
            }


            # send request
            if dataset_dict['name'] not in titles_ckan:
                response = requests.post(request,
                                        data=dataset_dict,
                                        headers=headers_dict
                                        )
            else:
                # post updated dataset

                # setup the request paramters:
                request2 = 'ad-server-ip/api/action/package_update'
                # send request
                response = requests.post(request2,
                                         data=dataset_dict,
                                         headers=headers_dict
                                         )

        response = HttpResponse('Export Plugin runs without any errors, check in Ckan for changes in datasets')
        return response

    def get_datasets(self):
        datasets = []
        for rdmo_dataset in self.get_set('project/dataset'):
            set_index = rdmo_dataset.set_index
            dataset = defaultdict(list)

            # file_name
            dataset['file_name'] = '{}.xml'.format(
                self.get_text('project/dataset/identifier', set_index=set_index) or
                self.get_text('project/dataset/id', set_index=set_index) or
                str(set_index + 1)
            )

            # identifier
            identifier = self.get_text('project/dataset/identifier', set_index=set_index)
            if identifier:
                dataset['identifier'] = identifier
                dataset['identifierType'] = \
                    self.get_option(self.identifier_type_options, 'project/dataset/identifier_type', set_index=set_index) or \
                    self.get_option(self.identifier_type_options, 'project/dataset/pids/system', set_index=set_index) or \
                    'OTHER'
            else:
                dataset['identifier'] = self.get_text('project/dataset/id')
                dataset['identifierType'] = 'OTHER'


            # titles
            dataset['titles'] = [{
                'title':
                    self.get_text('project/dataset/title', set_index=set_index) or
                    self.get_text('project/dataset/id', set_index=set_index) or
                    'Dataset #{}'.format(set_index + 1)
            }]

            # publisher
            publisher = \
                self.get_text('project/dataset/publisher', set_index=set_index) or \
                self.get_text('project/dataset/preservation/repository', set_index=set_index)
            if publisher:
                dataset['publisher'] = publisher

            # publication_year
            dataset['publicationYear'] = self.get_year('project/dataset/data_publication_date', set_index=set_index)

            # subjects
            subjects = \
                self.get_values('project/dataset/research/subject', set_index=set_index) or \
                self.get_values('project/research_field/title', set_index=set_index)
            if subjects:
                dataset['subjects'] = [{
                    'subject': subject.value
                } for subject in subjects]


            # dates
            dataset['created'] =  \
                self.get_timestamp('project/dataset/date/created', set_index=set_index)
            dataset['issued'] =  \
                self.get_timestamp('project/dataset/date/issued', set_index=set_index) or \
                self.get_timestamp('project/dataset/data_publication_date', set_index=set_index)

            # language
            dataset['language'] = self.get_option(self.language_options, 'project/dataset/language', set_index=set_index)

            # resource_type
            resource_type = self.get_text('project/dataset/resource_type', set_index=set_index)
            if resource_type:
                dataset['resourceType'] = resource_type
                dataset['resourceTypeGeneral'] = \
                    self.get_option(self.resource_type_general_options, 'project/dataset/resource_type_general', set_index=set_index)

            # rights
            for rights in self.get_values('project/dataset/sharing/conditions', set_index=set_index):
                dataset['rights_list'].append({
                    'rights': rights.value,
                    'rightsURI': self.rights_uri_options.get(rights.option.path)
                })

            # description
            description = self.get_text('project/dataset/description', set_index=set_index)
            if description:
                dataset['descriptions'] = [{
                    'description': description,
                    'descriptionType': 'Abstract'
                }]


            # contact point
            dataset['contactPoint'] = self.get_text('project/dataset/contactPoint', set_index=set_index)

            # description
            dataset['description'] = self.get_text('project/dataset/description', set_index=set_index)

            # spatial
            dataset['spatial'] = self.get_text('project/dataset/spatial', set_index=set_index)

            # theme
            dataset['theme'] = self.get_text('project/dataset/theme', set_index=set_index)

            # reference system
            dataset['conformsTo'] = self.get_text('project/dataset/conformsTo', set_index=set_index)

            # identifier

            datasets.append(dataset)

        return datasets

    def get_name(self, attribute, set_index=0, collection_index=0):
        name_text = self.get_text(attribute + '/name', set_index=set_index, collection_index=collection_index)
        if name_text:
            name = {
                'name': name_text,
                'nameType': self.get_option(self.name_type_options, attribute + '/name_type',
                                            set_index=set_index, collection_index=collection_index, default='Personal'),
            }

            # contributor_name
            contributor_type = self.get_option(self.contributor_type_options, attribute + '/contributor_type',
                                               set_index=set_index, collection_index=collection_index, default='Other')
            if contributor_type:
                name['contributorType'] = contributor_type

            # given_name
            given_name = self.get_text(attribute + '/given_name',
                                       set_index=set_index, collection_index=collection_index)
            if given_name:
                name['givenName'] = given_name

            # family_name
            family_name = self.get_text(attribute + '/family_name',
                                        set_index=set_index, collection_index=collection_index)
            if family_name:
                name['familyName'] = family_name

            # identifier
            identifier = self.get_text(attribute + '/identifier',
                                       set_index=set_index, collection_index=collection_index)
            if identifier:
                name['nameIdentifier'] = identifier
                name['nameIdentifierScheme'] = self.get_option(self.name_identifier_scheme_options,
                                                               attribute + '/identifier_type',
                                                               set_index=set_index, collection_index=collection_index,
                                                               default='ORCID')
            return name
        else:
            return None

