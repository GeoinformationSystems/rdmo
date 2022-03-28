Documentary (way to actual RDMO-instance)
written by: Tim Taugnitz,  Professur für Geoinformatik, TU Dresden, https://tu-dresden.de/bu/umwelt/geo/geoinformatik

Installation: 
- following the documentation of RDMO: https://rdmo.readthedocs.io/en/latest/index.html
- Add the IP-address in the local.py-file (in this case 172.26.62.135) at ALLOWED-HOSTS
- for TUD-VM: use the partition "data" on the VM

Deployment:
- install Apache
- following the documentation of RDMO: https://rdmo.readthedocs.io/en/latest/deployment/index.html

For debugging:
- set DEBUG = True in the local.py-file

Export-Format:
- create new folder in rdmo-app, named my_plugins
- create empty file” __init__.py” to make folder accessible for RDMO
- download export plugins from RDMO: https://rdmo.readthedocs.io/en/latest/configuration/plugins.html
- insert folder to my_plugins (use search functions to find the downloaded folder if necessary)
- create new plugin ckan.py in my_plugins/rdmo_plugins/export
- add Export possibilities to RDMO via the following lines:
PROJECT_EXPORTS.append(('datacite', _('as datacite'), 'my_plugins.rdmo_plugins.exports.datacite.DataCiteExport'))
PROJECT_EXPORTS.append(('ckan',_('to ckan'),'my_plugins.rdmo_plugins.exports.ckan.Ckan')) 

Creating Ckan-Plugin
- Description: The plugin links a metadata catalogue (here: a CKAN) with the RDMO software to enable researchers to manage dataset metadata and DMP in a single                tool. That facilitates researchers in managing metadata and DMP more efficient. When entering dataset metadata in a DMP via RDMO, the developed                  plugin copies relevant metadata and publish the metadata in the catalogue via catalogue API. We therefore modified a Science Europe template to                  fit to our developed metadata profile for geodata.

- copy code from datacite-plugin (datacite.py) to ckan.py
- changing class from DataCiteExport to Ckan
- write the API-request in the render function
- add the used attributes to the "get dataset"-function to make them reachable for the plugin
- OR: insert ckan.py (https://github.com/GeoinformationSystems/rdmo/edit/master/Tim_docs) to my_plugins
