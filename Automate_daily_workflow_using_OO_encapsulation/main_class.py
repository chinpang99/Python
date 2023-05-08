import pandas as pd
import numpy as np
from os import listdir
from os.path import isfile, join

list1 = []
class BAU_ABSA_QA_Task():
    @classmethod
    def absa_annotation_stage_1(cls, df: pd.DataFrame):
        no_of_annotation        = df.shape[0] 
        no_of_valid_annotation  = no_of_annotation - (df[df['last_output_0'] == 'Skip'].shape[0])  # no_of_invalid_annotation
        df["adjusted_amount"]   = ((df["content"].str.len())/240).apply(np.ceil)
        justified_valid_amount  = (df['adjusted_amount'].astype(np.int64).sum()) - (df[df['last_output_0'] == 'Skip']['adjusted_amount'].astype(np.int64).sum())  # justified_valid_amount
        qa_rate                 = '10%'
        no_of_qa_amount         = no_of_annotation * 0.1
        qa_pass_rate            = str(round((((no_of_qa_amount - (df[df['质检结果'] == '驳回'].shape[0])) / no_of_qa_amount)*100), 2)) + "%"
        df3                     = df[df['质检结果'] == '驳回'].groupby(['标注人ID'])['标注人ID'].size().reset_index(name='counts')
        df3['testing']          = df3['标注人ID'] + ": " + df3['counts'].astype(str) + " rejected case"
        df['testing']           = pd.DataFrame(['\n'.join(df3['testing'].to_list())], columns=['testing'])

        list1.append([no_of_annotation, no_of_valid_annotation, justified_valid_amount,
                     qa_rate, no_of_qa_amount, qa_pass_rate, df['testing'][0]])
        return list1

    @classmethod
    def rebutal(cls, df: pd.DataFrame):
        rebutal_df = df[df['质检结果'] == '驳回']
        return rebutal_df

    @classmethod
    def get_files(cls, date:str, input_dir:str):
        onlyfiles = [f for f in listdir(input_dir) if isfile(join(input_dir, f))]
        file_name = ''
        for i in onlyfiles:
            if date in i:
                file_name = i
                break
        
        return file_name
    