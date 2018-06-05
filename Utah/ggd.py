import os
from shutil import copy, copytree, rmtree, copy2, make_archive
from zipfile import ZipFile
import fiona
import geopandas as gpd
from arcgis.gis import GIS

from g_download import get_files
from agol import uploadArc

#folder where all the action takes place
WORKFOLDER = '../Utah_Nightly'

DOWNLOADING_FOLDER = os.path.join(WORKFOLDER,'download')
UPLOADING_FOLDER   = os.path.join(WORKFOLDER,'upload')
EXTRACTING_FOLDER  = os.path.join(WORKFOLDER,'extract')
WORKING_FOLDER     = os.path.join(WORKFOLDER,'sf_working')
PREVIOUS_FOLDER    = os.path.join(WORKFOLDER,'prev')


SLUG = '0ByStJjVZ7c7mM2hOYmF4ZENpNVE'

#create necessary folders for process
def create_dirs():
    if not os.path.exists(WORKFOLDER):
        os.mkdir(WORKFOLDER)
    assert(os.path.isdir(WORKFOLDER)) # might be plain ole file

    #clear out and remake the other folders
    if os.path.isdir(PREVIOUS_FOLDER):
        rmtree(PREVIOUS_FOLDER)

    if not os.path.isdir(EXTRACTING_FOLDER):
        os.mkdir(EXTRACTING_FOLDER)
    copytree(EXTRACTING_FOLDER, PREVIOUS_FOLDER)

    if os.path.isdir(UPLOADING_FOLDER):
        rmtree(UPLOADING_FOLDER)
    if os.path.isdir(DOWNLOADING_FOLDER):
        rmtree(DOWNLOADING_FOLDER)
    if os.path.isdir(WORKING_FOLDER):
        rmtree(WORKING_FOLDER)

    os.mkdir(UPLOADING_FOLDER)
    os.mkdir(DOWNLOADING_FOLDER)
    os.mkdir(WORKING_FOLDER)

    pass # out of create_dirs


def AddLinks(sf_name, src_dir, dest_dir):
    """
    Adds 3 urls to each feature in shape file, if shape file contains a column named 'API'.
    Writes shape file to destination folder and copies ancillary files from the source to the dest
    Arguments:
        sf_name: string, name of the shapefile, folder in src_dir
        src_dir: directory (folder) that contains sf_name
        dest_dir: directory (folder) where the modified shapefile is to be written
    """
    # variables to keep track of where things are coming and going:
    sf_path_in = os.path.join(src_dir, sf_name) # path to input shapefile directory
    sf_path_basename = os.path.join(sf_path_in, sf_name) # basename of the shapefile components
    sf_path_out = os.path.join(dest_dir, sf_name) # path to output shapefile directory

    # read up the shapefile
    gdf = gpd.read_file(sf_path_in)

    # get the schema:
    with fiona.open(sf_path_basename + '.shp') as f:
        input_schema = f.schema

    output_schema = input_schema
    outprops = output_schema['properties']

    # put on the links only if the shapefile has a column named 'API'
    if 'API' in gdf.columns:
        # put on the API10 column
        gdf['API10'] = gdf.API.str.slice(stop = 10)
        outprops.update({'API10':'str:10'})

        # Production history link
        gdf['Production'] = gdf.API10\
                        .apply(lambda s: 'https://oilgas.ogm.utah.gov/oilgasweb/live-data-search/lds-prod/prod-grid.xhtml?wellno={}'.format(s))
        outprops.update({'Production':'str:80'})
        
        # Well history link
        gdf['WellHistory'] = gdf.API10\
                        .apply(lambda s: 'https://oilgas.ogm.utah.gov/oilgasweb/live-data-search/lds-well/well-history-lu.xhtml?todo=srchIndvRow&api={}'.format(s))
        outprops.update({'WellHistory':'str:80'})
        
        # Well Logs link
        gdf['WellLogs'] = gdf.API10\
                        .apply(lambda s: 'https://oilgas.ogm.utah.gov/oilgasweb/live-data-search/lds-logs/logs-lu.xhtml?todo=srchIndvRow&api={}'.format(s))
        outprops.update({'WellLogs':'str:80'})

    # get the projection:
    prj_file = sf_path_basename + '.prj'
    prj = [l.strip() for l in open(prj_file,'r')][0]

    # write it back out
    output_schema['properties'] = outprops
    gdf.to_file(sf_path_out, crs_wkt=prj, schema = output_schema)

    # copy the .sbn, sbx and xml files from the source directory (sf_path_in) to the dest dir (sf_path_out)
    copy2(sf_path_basename + '.sbn', sf_path_out)
    copy2(sf_path_basename + '.sbx', sf_path_out)
    copy2(sf_path_basename + '.shp.xml', sf_path_out)

def ReZip(work_dir, sf_name, out_dir):
    make_archive(os.path.join(out_dir, sf_name),  "zip", work_dir, sf_name)



def main():
    
    # set up the directories
    create_dirs()

    #get the arcGis creds:
    try:
        gis = GIS(profile = "UtDOGM_Nightly_Profile")
    except:
        gis = GIS(url = "https://interfacegis.maps.arcgis.com/", username = input("Username: "), password = getpass(), profile = "UtDOGM_Nightly_Profile")


    #get the shapefiles to mash on
    shapefiles = get_files(SLUG, DOWNLOADING_FOLDER, EXTRACTING_FOLDER)
    
    #add links, zip up and upload each file
    for sf in shapefiles:
        AddLinks(sf, EXTRACTING_FOLDER, WORKING_FOLDER)
        ReZip(WORKING_FOLDER, sf, UPLOADING_FOLDER)
        uploadArc(gis, UPLOADING_FOLDER, sf, 'Nightly DOGM')

if __name__ == '__main__':
    main()
