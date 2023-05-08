from main_class import BAU_ABSA_QA_Task
import os 
import pandas as pd
import numpy as np
import xlsxwriter
from datetime import datetime
import csv
from xlsxwriter.workbook import Workbook

'''
Function    : Move files from local Downloads to WeDrive
Parameters  : csvfile (Dtype: String || Description: CSV File name)
Description : 1. Go to Downloads and copy the latest csv file name 
              2. Copy each row from the .csv to .xlsx
              3. Save the .xlsx file to WeDrive
Output      : The .csv file is saved as .xlsx in WeDrive
'''
def move_files_from_download_to_wedrive(csvfile:str):
    os.chdir('/Users/chinpangchia/Downloads')
    workbook = Workbook(csvfile[:-4] + '.xlsx')
    worksheet = workbook.add_worksheet()
    with open(csvfile, 'rt', encoding='utf8') as f:
        reader = csv.reader(f)
        for r, row in enumerate(reader):
            for c, col in enumerate(row):
                worksheet.write(r, c, col)
    os.chdir('/Users/chinpangchia/Library/')
    workbook.close()

if __name__ == "__main__":
    import argparse

    def init_args():
        parser = argparse.ArgumentParser()
        parser.add_argument("--taskID", default='0', type=str,help="Task ID of the task")
        args = parser.parse_args()

        return args
    
    args = init_args()
    list1 = []
    input_dir   = '/Users/chinpangchia/Library/'
    input_dir2  = '/Users/chinpangchia/Downloads/'
    date        = str(datetime.now().month) + str(datetime.now().day)
    date = args.taskID
    file_name   = BAU_ABSA_QA_Task.get_files(date, input_dir2) # Get CSV File name from Downloads
    file_name2  = BAU_ABSA_QA_Task.get_files(date, input_dir) # Get XLSX File name from WeDrive
    file_name3  = os.path.join(input_dir2, file_name2) # Check if the XLSX file in WeDrive is been uploaded anot
    if file_name3.split('.')[-1] == 'xlsx':
        print(file_name2 + " is exist ")
    else:
        move_files_from_download_to_wedrive(file_name)
        file_name2  = BAU_ABSA_QA_Task.get_files(date, input_dir) #Refresh and get the latest XLSX file from WeDrive

    
    #Data Processing: Read XLSX file from WeDrive and generate result for Rebutal & ABSA Tracking Log
    input_path  = os.path.join(input_dir, file_name2)
    print('Read ', input_path)
    df          = pd.read_excel(input_path)
    list1       = BAU_ABSA_QA_Task.absa_annotation_stage_1(df)
    list1       = np.reshape(list1,(-1,7))
    df2         = pd.DataFrame(list1, columns = ['no_of_annotation', 'no_of_valid_annotation', 'justified_valid_amount', 'qa_rate', 'no_of_qa_amount', 'qa_pass_rate', 'failed_summary'])

    rebutal_df = BAU_ABSA_QA_Task.rebutal(df)
    
    # Paste the result
    os.chdir('/Users/chinpangchia/Desktop/Python/BAU QA Task File')
    workbook = xlsxwriter.Workbook(file_name2)
    with pd.ExcelWriter(file_name2) as writer:
        df2.to_excel(writer, sheet_name='ABSA Annotation Stage 1', index= False)
        rebutal_df.to_excel(writer, sheet_name='rebutal', index=False)


