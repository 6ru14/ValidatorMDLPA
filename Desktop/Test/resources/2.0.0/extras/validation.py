import os
import re
import ast
import csv
import json
import fiona
import shutil
import zipfile
import logging
import pandas as pd
import numpy as np
import tempfile
from datetime import datetime
import filetype
import geopandas as gpd
from shapely.geometry import shape

from .writer import ReportWriter
from .rules import CategoryOne, CategoryTwo, CategoryThree, CategoryFour

class Validation:
    def __init__(self, tip_validare, zipfilepath, metadata, zfzrs, hilucs1, hilucs2, hilucs3):
        self.tip_validare = tip_validare
        self.zipfilepath = zipfilepath
        self.metadata = metadata
        self.zfzrs = zfzrs 
        self.hilucs1 = hilucs1
        self.hilucs2 = hilucs2
        self.hilucs3 = hilucs3
    
    def validate(self):
        category_1 = CategoryOne(validation_type = self.tip_validare, zip_path = self.zipfilepath)
        category_2 = CategoryTwo(validation_type = self.tip_validare, zip_path = self.zipfilepath)
        category_3 = CategoryThree(validation_type = self.tip_validare, zip_path = self.zipfilepath)
        category_4 = CategoryFour(validation_type = self.tip_validare, zip_path = self.zipfilepath)
        
        ReportWriter.clear_csv()
        ReportWriter.write_headers()
        
        validation_passed_list = []
        file_list, main_directory, folder_list, fisiere_list, avize_list, pdfs_list, gpkg_list, gdf = Validation.extract_data(zip_filepath=self.zipfilepath)
        validation_category = self.metadata.tip_validare_id.unique()
        
        for category in validation_category:
            category = int(category)
            
            if category == 1:
                rules = self.metadata[
                    (self.metadata['tip_validare_id'] == int(category)) & (self.metadata['categorie_regula_id'] == int(self.tip_validare))
                ].sort_values(by='numar_regula')

                for _, rule_dict in rules.iterrows():
                    try:
                        # Rule 1
                        if rule_dict['tip_regula_id'] == 1:
                            validation_passed = category_1.rule_1(
                                rule = rule_dict
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 2
                        if rule_dict['tip_regula_id'] == 2:
                            validation_passed = category_1.rule_2(
                                rule = rule_dict
                            )
                            validation_passed_list.append(validation_passed)
                            
                    except:
                        pass
            
            elif category == 2:
                rules = self.metadata[
                    (self.metadata['tip_validare_id'] == int(category)) & (self.metadata['categorie_regula_id'] == int(self.tip_validare))
                ].sort_values(by='numar_regula')

                for _, rule_dict in rules.iterrows():
                    try:
                        # Rule 3
                        if rule_dict['tip_regula_id'] == 3:
                            validation_passed = category_2.rule_3(
                                rule = rule_dict,
                                main_dir = main_directory
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 4
                        if rule_dict['tip_regula_id'] == 4:
                            validation_passed = category_2.rule_4(
                                rule = rule_dict,
                                main_dir = main_directory
                            )
                            validation_passed_list.append(validation_passed)
                            
                        # Rule 5
                        if rule_dict['tip_regula_id'] == 5:
                            validation_passed = category_2.rule_5(
                                rule = rule_dict,
                                folder_list = folder_list
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 6
                        if rule_dict['tip_regula_id'] == 6:
                            validation_passed = category_2.rule_6(
                                rule = rule_dict,
                                folder_list = folder_list
                            )
                            validation_passed_list.append(validation_passed)
                            
                        # Rule 7
                        if rule_dict['tip_regula_id'] == 7:
                            validation_passed = category_2.rule_7(
                                rule = rule_dict,
                                main_directory = main_directory,
                                file_list = file_list
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 8
                        if rule_dict['tip_regula_id'] == 8:
                            validation_passed = category_2.rule_8(
                                rule = rule_dict,
                                gpkg_list = gpkg_list
                            )
                            validation_passed_list.append(validation_passed)
                            
                        # Rule 9
                        if rule_dict['tip_regula_id'] == 9:
                            validation_passed = category_2.rule_9(
                                rule = rule_dict,
                                gpkg_list = gpkg_list
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 10
                        if rule_dict['tip_regula_id'] == 10:
                            validation_passed = category_2.rule_10(
                                rule = rule_dict,
                                pdfs_list = pdfs_list,
                                avize_list = avize_list
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 11
                        if rule_dict['tip_regula_id'] == 11:
                            validation_passed = category_2.rule_11(
                                rule = rule_dict,
                                pdfs_list = pdfs_list
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 12
                        if rule_dict['tip_regula_id'] == 12:
                            validation_passed = category_2.rule_12(
                                rule = rule_dict,
                                avize_list = avize_list
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 13
                        if rule_dict['tip_regula_id'] == 13:
                            validation_passed = category_2.rule_13(
                                rule = rule_dict,
                                avize_list = avize_list
                            )
                            validation_passed_list.append(validation_passed)
                            
                    except:
                        pass
            
            elif category == 3:
                rules = self.metadata[
                    (self.metadata['tip_validare_id'] == int(category)) & (self.metadata['categorie_regula_id'] == int(self.tip_validare))
                ].sort_values(by='numar_regula')

                for _, rule_dict in rules.iterrows():
                    try:
                        # Rule 14
                        if rule_dict['tip_regula_id'] == 14:
                            validation_passed = category_3.rule_14(
                                rule = rule_dict
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 15
                        if rule_dict['tip_regula_id'] == 15:
                            validation_passed = category_3.rule_15(
                                rule = rule_dict
                            )
                            validation_passed_list.append(validation_passed)
                    except:
                        pass
            
            elif category == 4:
                rules = self.metadata[
                    (self.metadata['tip_validare_id'] == int(category)) & (self.metadata['categorie_regula_id'] == int(self.tip_validare))
                ].sort_values(by='numar_regula')

                for _, rule_dict in rules.iterrows():
                    try:
                        # Rule 16
                        if rule_dict['tip_regula_id'] == 16:
                            validation_passed = category_4.rule_16(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                            
                        # Rule 17
                        if rule_dict['tip_regula_id'] == 17:
                            validation_passed = category_4.rule_17(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 18
                        if rule_dict['tip_regula_id'] == 18:
                            validation_passed = category_4.rule_18(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 19
                        if rule_dict['tip_regula_id'] == 19:
                            validation_passed = category_4.rule_19(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 20
                        if rule_dict['tip_regula_id'] == 20:
                            validation_passed = category_4.rule_20(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 21
                        if rule_dict['tip_regula_id'] == 21:
                            validation_passed = category_4.rule_21(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 22
                        if rule_dict['tip_regula_id'] == 22:
                            validation_passed = category_4.rule_22(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 23
                        if rule_dict['tip_regula_id'] == 23:
                            validation_passed = category_4.rule_23(
                                rule = rule_dict,
                                gdf = gdf,
                                cod_zf = self.zfzrs,
                                h1 = self.hilucs1,
                                h2 = self.hilucs2,
                                h3 = self.hilucs3
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 24
                        if rule_dict['tip_regula_id'] == 24:
                            validation_passed = category_4.rule_24(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                    
                        # Rule 25
                        if rule_dict['tip_regula_id'] == 25:
                            validation_passed = category_4.rule_25(
                                rule = rule_dict,
                                gdf = gdf,
                                h1 = self.hilucs1,
                                h2 = self.hilucs2,
                                h3 = self.hilucs3
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 26
                        if rule_dict['tip_regula_id'] == 26:
                            validation_passed = category_4.rule_26(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 27
                        if rule_dict['tip_regula_id'] == 27:
                            validation_passed = category_4.rule_27(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                            
                        # Rule 28
                        if rule_dict['tip_regula_id'] == 28:
                            validation_passed = category_4.rule_28(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 29
                        if rule_dict['tip_regula_id'] == 29:
                            validation_passed = category_4.rule_29(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 30
                        if rule_dict['tip_regula_id'] == 30:
                            validation_passed = category_4.rule_30(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 31
                        if rule_dict['tip_regula_id'] == 31:
                            validation_passed = category_4.rule_31(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)

                        # Rule 32
                        if rule_dict['tip_regula_id'] == 32:
                            validation_passed = category_4.rule_32(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 33
                        if rule_dict['tip_regula_id'] == 33:
                            validation_passed = category_4.rule_33(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 34
                        if rule_dict['tip_regula_id'] == 34:
                            validation_passed = category_4.rule_34(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 35
                        if rule_dict['tip_regula_id'] == 35:
                            validation_passed = category_4.rule_35(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                            
                        # Rule 36
                        if rule_dict['tip_regula_id'] == 36:
                            validation_passed = category_4.rule_36(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 37
                        if rule_dict['tip_regula_id'] == 37:
                            validation_passed = category_4.rule_37(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 38
                        if rule_dict['tip_regula_id'] == 38:
                            validation_passed = category_4.rule_38(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 39
                        if rule_dict['tip_regula_id'] == 39:
                            validation_passed = category_4.rule_39(
                                rule = rule_dict,
                                gdf = gdf,
                                zfzrs = self.zfzrs
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 40
                        if rule_dict['tip_regula_id'] == 40:
                            validation_passed = category_4.rule_40(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 41
                        if rule_dict['tip_regula_id'] == 41:
                            validation_passed = category_4.rule_41(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 42
                        if rule_dict['tip_regula_id'] == 42:
                            validation_passed = category_4.rule_42(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                        
                        # Rule 43
                        if rule_dict['tip_regula_id'] == 43:
                            validation_passed = category_4.rule_43(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                            
                        # Rule 44
                        if rule_dict['tip_regula_id'] == 44:
                            validation_passed = category_4.rule_44(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                        
                        #  Rule 45
                        if rule_dict['tip_regula_id'] == 45:
                            validation_passed = category_4.rule_45(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                        
                        #  Rule 46
                        if rule_dict['tip_regula_id'] == 46:
                            validation_passed = category_4.rule_46(
                                rule = rule_dict,
                                gdf = gdf
                            )
                            validation_passed_list.append(validation_passed)
                    except:
                        pass
            
        if False in validation_passed_list:
            validation_progress = False
        elif len(validation_passed_list) == 0:
            validation_progress = False
        else:
            validation_progress = True
        return validation_progress
    
    def extract_data(zip_filepath):
        with zipfile.ZipFile(zip_filepath, mode='r') as archive:
            file_list = archive.namelist()
            
            # To get the main directory
            main_directory = [folder.split('/')[0] for folder in file_list]
            main_directory = list(dict.fromkeys(main_directory))
            main_directory = list(filter(None, main_directory))
            
            folder_list = [folder.split('/')[1] for folder in file_list]
            folder_list = list(dict.fromkeys(folder_list))
            folder_list = list(filter(None, folder_list))
        
            fisiere_list = [file.split('/', 2)[-1] for file in file_list]
            fisiere_list = list(dict.fromkeys(fisiere_list))
            fisiere_list = list(filter(None, fisiere_list))
            
            avize = [item for item in fisiere_list if item.startswith("4_")]
            avize = [item for item in avize if item != ""]
        
            pdf_list = []
            for pdf in file_list:
                
                if pdf.endswith(".pdf"):
                    pdf_list.append(pdf)
                    
            pdfs_list = [pdf.split('/')[-1] for pdf in pdf_list]
        
            gpkg_list = []
            for gpkg in file_list:
                
                if gpkg.endswith('.gpkg'):
                    gpkg_list.append(gpkg)
            
            gpkg_list = [gpkg.split('/')[-1] for gpkg in gpkg_list]
        
            temp_dir = tempfile.mkdtemp()
            gpkg_path = []
    
            for gpkg in file_list:
                
                if gpkg.endswith('.gpkg'):
                    gpkg_path.append(gpkg)
            
            for gpkg in gpkg_path:
                archive.extract(gpkg, temp_dir)
                
            gpkg_file_path = os.path.join(temp_dir, gpkg)
            layers = fiona.listlayers(gpkg_file_path)
            gdf = {layer: gpd.read_file(gpkg_file_path, layer=layer) for layer in layers}
            shutil.rmtree(temp_dir)
            
            return file_list, main_directory, folder_list, fisiere_list, avize, pdfs_list, gpkg_list, gdf