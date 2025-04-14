import os
import re
import numpy as np
import pandas as pd
from shapely.geometry import shape
from pyproj import Geod
import zipfile
import tempfile
from datetime import datetime
import filetype
import fiona
from .writer import ReportWriter
from .database import APIClient, AuthManager, ConfigManager
# 1 - PUG | 2 - PUD | 3 - PUZ | 4 - PATJ

class CategoryOne:
    def __init__(self, validation_type, zip_path):
        self.validation_type = validation_type 
        self.zip_path = zip_path
    
    # Rule 1 - Checks if the file exists
    def rule_1(self, rule):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                if not os.path.exists(self.zip_path):
                    ReportWriter.write_fail(rule=rule, verify=self.zip_path)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
                
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1  # False only if Blocker
    
    # Rule 2 - Checks if the file is a zip
    def rule_2(self, rule):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                if not zipfile.is_zipfile(self.zip_path):
                    ReportWriter.write_fail(rule=rule, verify=self.zip_path)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
                
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1  # False only if Blocker
    
class CategoryTwo:
    def __init__(self, validation_type, zip_path):
        self.validation_type = validation_type 
        self.zip_path = zip_path
    
    # Checks if only one main directory exists
    def rule_3(self, rule, main_dir):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                if not int(rule["valoare_regula"]) == int(len(main_dir)):
                    ReportWriter.write_fail(rule=rule, verify=rule["valoare_regula"])
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
            
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1
    
    # Checks if the name of the dir is correct
    def rule_4(self, rule, main_dir):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                if len(main_dir) != 1:
                    ReportWriter.write_fail(rule=rule, verify=f"Au fost gasite {len(main_dir)} directoare principale! Trebuie sa fie doar un singur director principal")
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                # Get the directory and regex
                directory = main_dir[0]
                regex = rule['valoare_regula']
                
                if not re.match(regex, directory):
                    ReportWriter.write_fail(rule=rule, verify=main_dir)
                    return int(rule['tip_alerta_id']) != 1 # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
                
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1
    
    # Checks if the number of subdirs is correct
    def rule_5(self, rule, folder_list):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                if not int(rule["valoare_regula"]) == int(len(folder_list)):
                    ReportWriter.write_fail(rule=rule, verify=rule["valoare_regula"])
                    return int(rule['tip_alerta_id']) != 1 # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
                
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
        
    # Checks if the subdirs names are correct
    def rule_6(self, rule, folder_list):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                if not rule["valoare_regula"] in folder_list:
                    ReportWriter.write_fail(rule=rule, verify=rule["valoare_regula"])
                    return int(rule['tip_alerta_id']) != 1 # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
            
    # Checks if the main dir, subdir and files have the correct structure
    def rule_7(self, rule, main_directory, file_list):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                main_dir = main_directory[0]
                expected_folders = rule['valoare_regula'].split(',')

                for folder in expected_folders:
                    folder_structure = f'{main_dir}/{folder}/'
                    if folder_structure not in file_list:
                        ReportWriter.write_fail(
                            rule=rule,
                            verify=f"Folder '{folder_structure}' not found in file list"
                        )
                        return int(rule['tip_alerta_id']) != 1 # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the number of gpkg is correct
    def rule_8(self, rule, gpkg_list):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                if not int(rule["valoare_regula"]) == int(len(gpkg_list)):
                    ReportWriter.write_fail(rule=rule, verify=rule["valoare_regula"])
                    return int(rule['tip_alerta_id']) != 1 # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the gpkg has the correct name structure  
    def rule_9(self, rule, gpkg_list):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                if len(gpkg_list) != 1:
                    ReportWriter.write_fail(rule=rule, verify=f"Au fost gasite {len(gpkg_list)} fisiere gpkg! Trebuie sa fie doar un singur fisier gpkg!")
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                gpkg = gpkg_list[0]
                regex = rule['valoare_regula']
                
                if not re.match(regex, gpkg):
                    ReportWriter.write_fail(rule=rule, verify=gpkg)
                    return int(rule['tip_alerta_id']) != 1
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the number of pdfs is correct (w/o avize)
    def rule_10(self, rule, pdfs_list, avize_list):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                if not int(rule["valoare_regula"]) >= int(len(pdfs_list)) - int(len(avize_list)):
                    ReportWriter.write_fail(rule=rule, verify=rule["valoare_regula"])
                    return int(rule['tip_alerta_id']) != 1 # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
      
    # Checks if the pdf files names are correct   
    def rule_11(self, rule, pdfs_list):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                if not rule["valoare_regula"] in pdfs_list:
                    ReportWriter.write_fail(rule=rule, verify=rule["valoare_regula"])
                    return int(rule['tip_alerta_id']) != 1 # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the number of pdfs (avize) is correct
    def rule_12(self, rule, avize_list):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                if not int(rule["valoare_regula"]) >= int(len(avize_list)):
                    ReportWriter.write_fail(rule=rule)
                    return int(rule['tip_alerta_id']) != 1 # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the name of the pdfs (avize) is correct
    def rule_13(self, rule, avize_list):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                regex = rule['valoare_regula']
                avize_failed = []
                
                for aviz in avize_list:
                    if not re.match(r''+regex+'', aviz):
                        avize_failed.append(aviz)
                        
                if not len(avize_failed) == 0:
                    ReportWriter.write_fail(rule=rule, verify=avize_failed)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
            
class CategoryThree:
    def __init__(self, validation_type, zip_path):
        self.validation_type = validation_type 
        self.zip_path = zip_path
    
    # Checks if the pdfs files are valid 
    def rule_14(self, rule):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                rule_value = []
                pdf_fail = []
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    with zipfile.ZipFile(self.zip_path, 'r') as zip_archive:
                        pdf_files = [pdf for pdf in zip_archive.namelist() if pdf.lower().endswith('.pdf')]
                        zip_archive.extractall(temp_dir, members=pdf_files)
                        
                        for pdf_file in pdf_files:
                            extract_path = os.path.join(temp_dir, pdf_file)
                            
                            kind = filetype.guess(extract_path)
                            if kind == None:
                                pdf_fail.append(pdf_file)
                                rule_value.append(False)
                            
                            elif kind.extension != rule["valoare_regula"]:
                                pdf_fail.append(pdf_file)
                                rule_value.append(False)
                            
                            elif kind.extension == rule["valoare_regula"]:
                                rule_value.append(True)
                            
                            else:
                                pdf_fail.append(pdf_file)
                                rule_value.append(False)
                
                pdf_fail_list = [pdf.split('/')[-1] for pdf in pdf_fail]
                pdf_fail_list = '\n'.join(pdf_fail_list) 
                
                if False in rule_value:
                    ReportWriter.write_fail(rule=rule, verify=pdf_fail_list)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the gpkg file is valid
    def rule_15(self, rule):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                rule_value = []
                    
                with tempfile.TemporaryDirectory() as temp_dir:
                    with zipfile.ZipFile(self.zip_path, 'r') as zip_archive:
                        gpkg_files = [gpkg for gpkg in zip_archive.namelist() if gpkg.lower().endswith('.gpkg')]
                        zip_archive.extractall(temp_dir, members=gpkg_files)
                        
                        for gpkg_file in gpkg_files:
                            extract_path = os.path.join(temp_dir, gpkg_file)
                            
                            with fiona.open(extract_path) as src:
                                file_format = src.driver.lower()
                                
                                if file_format == None:
                                    rule_value.append(False)
                            
                                elif file_format != rule["valoare_regula"]:
                                    rule_value.append(False)
                            
                                elif file_format == rule['valoare_regula']:
                                    rule_value.append(True)
                            
                                else:
                                    rule_value.append(False)
                         
                if False in rule_value:
                    ReportWriter.write_fail(rule=rule, verify=gpkg_files)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                                    
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
class CategoryFour:
    def __init__(self, validation_type, zip_path):
        self.validation_type = validation_type 
        self.zip_path = zip_path
    
    # Checks if there are the correct number of layers
    def rule_16(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                if not int(rule["valoare_regula"]) <= int(len(gdf)):
                    ReportWriter.write_fail(rule=rule)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks the gpkg has the layer specified
    def rule_17(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                if not rule["valoare_regula"] in gdf.keys():
                    ReportWriter.write_fail(rule=rule)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
            
    # Checks if the number of columns from the layers is correct
    def rule_18(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                layer = rule['formula_regula']
                column_number = rule['valoare_regula']
                
                columns: list = gdf[layer].columns.to_list()
                
                if 'geometry' in columns:
                    columns.remove('geometry')
                
                if not int(column_number) <= int(len(columns)):
                    ReportWriter.write_fail(rule=rule)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the columns have the correct names in every layer
    def rule_19(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                rule_value = []
                columns_nf = []
                
                layer = rule['formula_regula']
                column_names = rule['valoare_regula'].split(',')
                
                columns: list = gdf[layer].columns.to_list()
                
                if 'geometry' in columns:
                    columns.remove('geometry')
                    
                for column_name in column_names:
                    if not column_name in columns:
                        rule_value.append(False)
                        columns_nf.append(column_name)
                        
                if False in rule_value:
                    ReportWriter.write_fail(rule=rule, verify=columns_nf)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the layer contains data (the layers isn't empty)
    def rule_20(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                if len(gdf[rule['formula_regula']]) == 0:
                    ReportWriter.write_fail(rule=rule, verify=rule['formula_regula'])
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the columns contain data (are not empty)
    def rule_21(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                columns_null = {}
                
                layer = rule['formula_regula']
                columns: list = rule['valoare_regula'].split(',')
                special_columns = ["POT", "CUT", "CLAD"]
                
                for column in columns:
                    col_data = gdf[layer][column]
                    
                    null_indices = [
                        i + 1 for i, value in enumerate(col_data)
                        if value in [None, "", "NULL"] or (isinstance(value, float) and np.isnan(value))
                    ]
                    
                    if column in special_columns and len(null_indices) == len(col_data):
                        columns_null[column] = "Nu contine date!"
                    elif null_indices and column not in special_columns:
                        columns_null[column] = null_indices
                
                if len(columns_null) != 0:
                    ReportWriter.write_fail(rule=rule, verify=columns_null)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the dtype of the data is correct
    def rule_22(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                rule_value = []
                columns_wd =[]
                
                layer = rule['formula_regula']
                columns_dtypes = rule['valoare_regula'].split(',')
                
                for column_dtype in columns_dtypes:
                    column, dtype = column_dtype.split('-')
                    
                    if gdf[layer][column].dtype == dtype:
                        rule_value.append(True)
                    else:
                        if gdf[layer][column].dtype == 'O':
                            
                            gdf[layer][column] = pd.to_datetime(gdf[layer][column], errors='coerce')
                            gdf[layer][column] = gdf[layer][column].astype('datetime64[ms]')
                            
                            if gdf[layer][column].dtype == dtype:
                            
                                rule_value.append(True)
                            
                            else:
                                rule_value.append(False)
                                columns_wd.append(column)
                                columns_wd.append(dtype)
                                columns_wd.append(gdf[layer][column].dtype)
                
                if False in rule_value:
                    ReportWriter.write_fail(rule=rule, verify=columns_wd)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                                    
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the data has the correct name/structure inside the layer columns
    def rule_23(self, rule, gdf, cod_zf, h1, h2, h3):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                columns_wd = {}
                
                layer = rule['formula_regula']
                data: str = rule['valoare_regula']
                
                columns_dtypes: list = data.split(',')
                
                for column_dtype in columns_dtypes:
                    column, dtype = column_dtype.split('-')
                    col_data = gdf[layer][column]
                    if dtype == 'check_cod':
                        wrong_data = [
                            i + 1 for i, value in enumerate(col_data)
                            if value is not None and not (isinstance(value, float) and np.isnan(value))
                            and not value in cod_zf['definitie'].to_list()
                        ]
                    elif dtype == 'check_h1':
                        wrong_data = [
                            i + 1 for i, value in enumerate(col_data)
                            if value is not None and not (isinstance(value, float) and np.isnan(value))
                            and not value in h1['definitie'].to_list()
                        ]
                    elif dtype == 'check_h2':
                        wrong_data = [
                            i + 1 for i, value in enumerate(col_data)
                            if value is not None and not (isinstance(value, float) and np.isnan(value))
                            and not value in h2['definitie'].to_list()
                        ]
                    elif dtype == 'check_h3':
                        wrong_data = [
                            i + 1 for i, value in enumerate(col_data)
                            if value is not None and not (isinstance(value, float) and np.isnan(value))
                            and not value in h3['definitie'].to_list()
                        ]
                    elif dtype == 'Date':
                        wrong_data = [
                            i + 1 for i, value in enumerate(col_data)
                            if value is not None and not (isinstance(value, float) and np.isnan(value))
                            and not re.match(r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])(?: 00:00:00(?:\+00:00)?)?$', str(value).strip())
                        ]
                    elif dtype == 'Date_2':
                        wrong_data = [
                            i + 1 for i, value in enumerate(col_data)
                            if value is not None and not (isinstance(value, float) and np.isnan(value))
                            and not re.match(r'^\d{1,6}\/(0[1-9]|[1-2][0-9]|3[0-1])\.(0[1-9]|1[0-2])\.\d{4}$', str(value).strip())
                        ]
                    elif dtype == 'Zecimale':
                        wrong_data = [
                            i + 1 for i, value in enumerate(col_data)
                            if value is not None and not (isinstance(value, float) and np.isnan(value))
                            and not re.match(r'^\d*\.\d{1,2}$', str(value))
                        ]
                    elif dtype == 'HCL':
                        wrong_data = [
                            i + 1 for i, value in enumerate(col_data)
                            if value is not None and not (isinstance(value, float) and np.isnan(value))
                            and not re.match(r'^\d{1,6}$', str(value))
                        ]
                    else:
                        item_list = dtype.split('_')
                        wrong_data = [
                            i + 1 for i, value in enumerate(col_data)
                            if value is not None and not (isinstance(value, float) and np.isnan(value))
                            and value not in item_list
                        ]
                    
                    if wrong_data:
                        columns_wd[column] = wrong_data
                        ReportWriter.write_fail(rule=rule, verify=columns_wd)
                        return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                            
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the temporial data is correct    
    def rule_24(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                layer = rule['formula_regula']
                columns: list = rule['valoare_regula'].split(",")
                current_date = datetime.now()
                
                if "Data_aprob" in columns and "Data_exp" in columns:
                    index_fail = [
                        i + 1 
                        for i in range(len(gdf[layer]['Data_aprob']))
                        if not (gdf[layer]['Data_aprob'][i] <= current_date <= gdf[layer]['Data_exp'][i])
                    ]
                
                elif "Data_exp" in columns and len(columns) == 1:
                    index_fail = [
                        i + 1 
                        for i in range(len(gdf[layer]['Data_exp']))
                        if not (current_date >= gdf[layer]['Data_exp'][i])
                    ]
                
                elif "Revizie" in columns and len(columns) == 1:
                    index_fail = [
                        i + 1 
                        for i in range(len(gdf[layer]['Revizie']))
                        if not (current_date >= gdf[layer]['Revizie'][i])
                    ]
            
                if index_fail:
                    ReportWriter.write_fail(rule=rule, verify=index_fail)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                    
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the hilucs hierarchy and names are correct
    def rule_25(self, rule, gdf, h1, h2, h3):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                index_fail = set()
                
                layer = rule['formula_regula']
                columns = rule['valoare_regula'].split(',')
                
                h1_list = list(h1['definitie'])
                h2_list = list(h2['definitie'])
                h3_list = list(h3['definitie'])

                for i in range(len(gdf[layer])):
                    hilucs_1 = gdf[layer][columns[0]][i]
                    hilucs_2 = gdf[layer][columns[1]][i]
                    hilucs_3 = gdf[layer][columns[2]][i]
                    
                    h1_class = re.sub(r'[^\d_]', '', hilucs_1) if hilucs_1 is not None else ""
                    h2_class = re.sub(r'[^\d_]', '', hilucs_2) if hilucs_2 is not None else ""
                    
                    if hilucs_1 not in h1_list:
                        index_fail.add(i + 1)
                        
                    if hilucs_2 is not None:
                        if h1_class not in hilucs_2 or hilucs_2 not in h2_list:\
                            index_fail.add(i + 1)
                    
                    if hilucs_3 is not None:
                        if h2_class not in hilucs_3 or hilucs_3 not in h3_list:
                            index_fail.add(i + 1)

                if index_fail:
                    ReportWriter.write_fail(rule=rule, verify=index_fail)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if codes from a layers column coincide with codes from another layers column
    def rule_26(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                column_fail = {}
                index_fail = []
                
                layer_1, column_1 = rule['formula_regula'].split(":")
                layer_2, column_2 = rule['valoare_regula'].split(":")
                
                cods = gdf[layer_1][column_1].to_list()
                to_check = gdf[layer_2][column_2].to_list()

                for i in range(len(to_check)):
                    if to_check[i] not in cods:
                        index_fail.append(i+1)
                
                if index_fail:
                    column_fail[column_2] = index_fail
                    ReportWriter.write_fail(rule=rule, verify=column_fail)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                    
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the gpkg has the correct crs
    def rule_27(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                layer = rule['formula_regula']
                gdf_crs = gdf[layer]['geometry'].crs 

                if not gdf_crs == rule['valoare_regula']:
                    ReportWriter.write_fail(rule=rule)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                    
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the layers have geometries
    def rule_28(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                layer = rule['formula_regula']
                
                if gdf[layer]['geometry'].empty:
                    ReportWriter.write_fail(rule=rule)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                    
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the layer geometries are not NULL
    def rule_29(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                layer = rule['formula_regula']
                column_data = gdf[layer]['geometry']
                
                index_fail = [
                    i + 1 for i, geom in enumerate(column_data)
                    if geom is None or geom == "" or (isinstance(geom, float) and np.isnan(geom))
                ]
                
                if index_fail:
                    ReportWriter.write_fail(rule=rule, verify=index_fail)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                    
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the layers have the correct geometry type
    def rule_30(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                layer = rule['formula_regula']
                geom_type = rule['valoare_regula']
                
                if not gdf[layer].geom_type.to_list()[0] == geom_type:
                    ReportWriter.write_fail(rule=rule, verify=geom_type)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                    
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the layer geometries are valid
    def rule_31(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                layer = rule['formula_regula']
                column_data = gdf[layer]['geometry']
                
                index_fail = [
                    i + 1 for i in range(len(column_data))
                    if not column_data.iloc[i].is_valid
                ]
                
                if index_fail:
                    ReportWriter.write_fail(rule=rule, verify=index_fail)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                    
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the PlanSpatial is inside the UAT limit
    def rule_32(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 4]:
            try:
                layer = rule['formula_regula']
                column_siruta = rule['valoare_regula']
                
                uat_db = APIClient(ConfigManager(), AuthManager(ConfigManager())).get_geodata(siruta = gdf[layer][column_siruta][0])
                
                if uat_db is None:
                    rule_value = False
                else:
                    gdf_boundary = gdf[layer]['geometry'].boundary
                    uat_db_boundary = uat_db.boundary
                    
                    target_crs = gdf[layer]['geometry'].crs
                    
                    gdf_boundary = gdf_boundary.set_crs(target_crs)
                    uat_db_boundary = uat_db_boundary.set_crs(target_crs)
                    uat_db_boundary_buffered = uat_db_boundary.buffer(10)
                    
                    rule_value = gdf_boundary.within(uat_db_boundary_buffered).all()
                    
                if rule_value == False:
                    ReportWriter.write_fail(rule=rule)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                    
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
        
        elif int(self.validation_type) == 3:
            try:
                layer = rule['formula_regula']
                column_siruta = rule['valoare_regula']
                
                uat_db = APIClient(ConfigManager(), AuthManager(ConfigManager())).get_geodata(siruta = gdf[layer][column_siruta][0])
    
                if uat_db is None:
                    rule_value = False
                else:
                    rule_value = uat_db.geometry.contains(gdf[layer]["geometry"]).all()
                    
                if rule_value == False:
                    ReportWriter.write_fail(rule=rule)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Verifies if a layers geometries are inside the PlanSpatial
    def rule_33(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                layer_tfi = rule['formula_regula']
                layer_tbi = rule['valoare_regula']
                
                geom_tbi = gdf[layer_tbi]['geometry'][0]
                geom_tfi = gdf[layer_tfi]['geometry']
                
                index_fail = [
                    i + 1 for i, geom in enumerate(geom_tfi)
                    if not geom.within(geom_tbi.buffer(0.1))
                ]
                
                if index_fail:
                    ReportWriter.write_fail(rule=rule)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                    
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if some layers cover the PlanSpatial completely
    def rule_34(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                layer_to_cover = rule['formula_regula']
                layer_to_be_covered = rule['valoare_regula']
                
                column_data = gdf[layer_to_cover]['geometry']
                geom = gdf[layer_to_be_covered]['geometry'][0]
                
                rule_value = geom.area - 50 <= column_data.unary_union.area
                
                if rule_value == False:
                    ReportWriter.write_fail(rule=rule)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the layers geometries overlap
    def rule_35(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                overlap_pairs = []
                unique_pairs = set()
                filtered_pairs = []
                
                layer = rule['formula_regula']
                column_data = gdf[layer]['geometry']
                
                sindex = column_data.sindex
                
                for i, geom in enumerate(column_data):
                    bbox = geom.bounds
                    overlaps = list(sindex.intersection(bbox))
                    
                    for j in overlaps:
                        if i != j and geom.overlaps(column_data.iloc[j]):
                            overlap_pairs.append((int(i+1), int(j+1)))
                
                if overlap_pairs:
                    rule_value = False
                    for pair in overlap_pairs:
                        sorted_pair = tuple(sorted(pair))

                        if sorted_pair not in unique_pairs:
                            filtered_pairs.append(pair)
                            unique_pairs.add(sorted_pair)
                else:
                    rule_value = True
                    
                if rule_value == False:
                    ReportWriter.write_fail(rule=rule, verify=filtered_pairs)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
            
    # Checks if the polygons are sliver polygons
    def rule_36(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                area_threshold = 1e-6  
                aspect_ratio_threshold = 10 
                
                layer = rule['formula_regula']
                
                column_data = gdf[layer]['geometry']
                
                index_fail = [
                    i + 1 for i, geom in enumerate(column_data.dropna())
                    if geom.area < area_threshold 
                    and (geom.length / geom.area if geom.area > 0 else float('inf')) > aspect_ratio_threshold
                ]
                
                if index_fail:
                    ReportWriter.write_fail(rule=rule, verify=index_fail)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if codes are unique
    def rule_37(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                list_of_codes = []
                index_fail = []
                
                layer = rule['formula_regula']
                cod_column = rule['valoare_regula']
                
                column_data = gdf[layer][cod_column]
                
                for i, code in enumerate(column_data):
                    if code in list_of_codes:
                        index_fail.append( i+1 )
                    else:
                        list_of_codes.append(code)
                
                if index_fail:
                    ReportWriter.write_fail(rule=rule, verify=index_fail)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                    
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the columns from a layer have the same values on a row
    def rule_38(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                column_fail = {}
                index_fail = []
                
                layer_1, column_1 = rule['formula_regula'].split(":")
                layer_2, column_2 = rule['valoare_regula'].split(":")
                
                cods = gdf[layer_1][column_1].to_list()
                to_check = gdf[layer_2][column_2].to_list()

                for i in range(len(to_check)):
                    if to_check[i] in cods:
                        index_fail.append(i+1)
                
                if index_fail:
                    column_fail[column_2] = index_fail
                    ReportWriter.write_fail(rule=rule, verify=column_fail)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                    
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the romanian words are correct
    def rule_39(self, rule, gdf, zfzrs):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                index_fail = []
                
                layer = rule['formula_regula']
                cod, tip = rule['valoare_regula'].split(',')
                
                cod_column = gdf[layer][cod]
                tip_column = gdf[layer][tip]
                
                romanian_map = {
                    '\u015F': '\u0219',  # ş -> ș
                    '\u0163': '\u021B',  # ţ -> ț
                }
                
                for i in range(len(cod_column)):
                    cod_zf_zrs = cod_column[i]
                    tip_zf_zrs = tip_column[i]
                    
                    row = np.where(zfzrs['definitie'] == cod_zf_zrs)[0][0]
                    to_check = zfzrs['definite_lung'][row].strip()
                    for old_char, new_char in romanian_map.items():
                        tip_zf_zrs = tip_zf_zrs.replace(old_char, new_char)
                        element_check = to_check.replace(old_char, new_char)  
                    
                    if tip_zf_zrs.strip() != element_check:
                        index_fail.append(i+1)
                
                if index_fail:
                    ReportWriter.write_fail(rule=rule, verify=index_fail)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the dates are the same in a layer's column
    def rule_40(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                index_fail = []
                
                layer = rule['formula_regula']
                columns = [rule['valoare_regula']] if ',' not in rule['valoare_regula'] else rule['valoare_regula'].split(',')
                
                for column in columns:
                    value_list = gdf[layer][column].to_list()
                    unique_values = list(set(value_list))
                    
                    if len(unique_values) != 1:
                        values = {}
                        for value in unique_values:
                            numb_val = value_list.count(value)
                            values[value] = numb_val
                
                        max_value = max(values.values())
                        ids_to_get = [key for key, value in values.items() if value != max_value]

                        for i in range(len(gdf[layer][column])):
                            time_to_check = gdf[layer][column][i]
                            if time_to_check in ids_to_get:
                                index_fail.append(i+1)
                
                if index_fail:
                    ReportWriter.write_fail(rule=rule, verify=index_fail)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                    
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the geometries has only x and y coordinates
    def rule_41(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                layer = rule['formula_regula']
                column_data = gdf[layer]['geometry']
                
                index_fail = [
                    i + 1 for i, geom in enumerate(column_data)
                    if geom is not None and geom.has_z
                ]
                
                if index_fail:
                    ReportWriter.write_fail(rule=rule, verify=index_fail)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the geometry area is the same as the area specified in the layer's column
    def rule_42(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                index_fail = []
                
                layer, unit = rule['formula_regula'].split('-')
                column = rule['valoare_regula']
                
                column_data = gdf[layer][column]
                geometry_data = gdf[layer]["geometry"]
                    
                for i in range(len(geometry_data)):
                    if unit == 'ha':
                        value = round(geometry_data[i].area, 2) / 10000
                    elif unit == 'm':
                        value = round(geometry_data[i].area, 2)
                        
                    result = abs(value - float(column_data[i]))
                    value_1 = float(f'{result:.2f}')
                    within_tolerance = value_1 <= 0.1
                    
                    if within_tolerance == False:
                        index_fail.append(i + 1)
                        
                if index_fail:
                    ReportWriter.write_fail(rule=rule, verify=index_fail)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the geometry length is the same as the length specified in the layer's column
    def rule_43(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                index_fail = []
                layer = rule['formula_regula']
                column = rule['valoare_regula']
                
                column_data = gdf[layer][column]
                geometry_data = gdf[layer]["geometry"]
                
                for i in range(len(geometry_data)):
                    value = round(geometry_data[i].length, 2)
                    
                    result = abs(value - float(column_data[i]))
                    value = float(f'{result:.2f}')
                    within_tolerance = value <= 0.1
                    
                    if within_tolerance == False:
                        index_fail.append(i + 1)
                
                if index_fail:
                    ReportWriter.write_fail(rule=rule, verify=index_fail)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the sum of the geometries area is the same as the area of the PlanSpatial geometry
    def rule_44(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                layer_1, col_1 = rule['formula_regula'].split('-')
                layer_2, col_2 = rule['valoare_regula'].split('-')
                
                column_data_1 = gdf[layer_1][col_1]
                column_data_2 = gdf[layer_2][col_2]
                
                area_1 = 0
                area_2 = 0
                
                for index, value in enumerate(column_data_1):
                    area_1 +=value
                for index, value in enumerate(column_data_2):
                    area_2 +=value                    
                
                result = abs(area_1 - area_2)
                value = float(f'{result:.2f}')
                within_tolerance = value <= 0.1
                
                if not within_tolerance:
                    ReportWriter.write_fail(rule=rule)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
    
    # Checks if the PlanSpatial has the correct SIRUTA
    def rule_45(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                uat = APIClient(ConfigManager(), AuthManager(ConfigManager())).get_geodata(siruta=gdf[rule['formula_regula']][rule['valoare_regula']][0])
                
                if uat is None:
                    ReportWriter.write_fail(rule=rule)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker
      
    # Checks if the data coresponds from one table to another      
    def rule_46(self, rule, gdf):
        if int(self.validation_type) in [1, 2, 3, 4]:
            try:
                index_fail = []
                
                romanian_map = {
                    '\u015F': '\u0219',  # ş -> ș
                    '\u0163': '\u021B',  # ţ -> ț
                }
                
                layer_1, columns_1 = rule['formula_regula'].split('-')
                cod_1, tip_1, zona_1 = columns_1.split(',')
                
                layer_2, columns_2 = rule['valoare_regula'].split('-')
                cod_2, tip_2, zona_tip = columns_2.split(',')
                
                gdf_l1_c1 = gdf[layer_1][cod_1]
                gdf_l1_t1 = gdf[layer_1][tip_1]
                gdf_l1_z1 = gdf[layer_1][zona_1]
                
                gdf_l2_c2 = gdf[layer_2][cod_2]
                gdf_l2_t2 = gdf[layer_2][tip_2]
                
                for i in range(len(gdf_l1_t1)):
                    if gdf_l1_c1[i] in gdf_l2_c2.to_list():
                        if gdf_l1_t1[i].strip() not in [element.strip() for element in gdf_l2_t2]:
                            index_fail.append(i+1)                            
                        
                        for old_char, new_char in romanian_map.items():
                            zona_tip_element = zona_tip.replace(old_char, new_char).strip()
                            gdf_l1_z1_element = gdf_l1_z1[i].replace(old_char, new_char).strip()
                        
                        if zona_tip_element != gdf_l1_z1_element:
                            index_fail.append(i+1)                                    
                        
                if index_fail:
                    ReportWriter.write_fail(rule=rule, verify=index_fail)
                    return int(rule['tip_alerta_id']) != 1  # False only if Blocker
                
                ReportWriter.write_pass(rule=rule)
                return True
            except Exception as e:
                ReportWriter.write_error(rule=rule, verify=str(e))
                return int(rule['tip_alerta_id']) != 1 # False only if Blocker