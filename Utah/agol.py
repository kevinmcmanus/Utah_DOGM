# agol.py - bunch of functions for uploading content to ArcGIS Online
import os
from os import path
import time
from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection

def uploadArc(gis, ziproot, sf_name, folder_name):
    #print("\nUpload UtDOGM files to ArcGIS Online directory at: " + time.asctime() + "\n\n")

    gis.content.create_folder(folder_name)
    zipname = os.path.join(ziproot,sf_name)+'.zip'

    def add():
        time.sleep(5)
        gis.content.add(item_properties = {"type": "Shapefile"},
                        data = zipname,
                        folder = folder_name)
        print("\t" + sf_name + " was uploaded.\n")
        
    def publish():
        time.sleep(5)
        file = gis.content.search(query = "title:{} AND type:{}".format(sf_name,"Shapefile"))
        file = file[0]
        file.publish(publish_parameters = {"name": sf_name + "_published", "maxRecordCount": 2000}).layers[0]
        print("\t" + sf_name + " was published.\n")
    
    # find file in list of files
    def findfile(files, filetitle):
        f = None
        for i in range(len(files)):
            if files[i].title == filetitle:
                f = files[i]
                break
                
        assert(f is not None)
        return f
      

    file  = gis.content.search(query = "title:{} AND type:{}".format(sf_name,"Shapefile"))
    file2 = gis.content.search(query = "title:{} AND type:{}".format(sf_name,"Feature"))
    if (len(file) is 0) or (len(file2) is 0):
        if len(file) is 0:
            add()
        if len(file2) is 0:
            publish()
    else:
        print("\toverwriting: " + sf_name + "\n" )
        filelist = gis.content.search(query = "title:{} AND type:{}".format(sf_name,"Feature"))
        file = findfile(filelist, sf_name)
        newfile = FeatureLayerCollection.fromitem(file)
        newfile.manager.overwrite(zipname)
        print("\t" + sf_name + " was overwritten.\n")
            