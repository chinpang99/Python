from annotator import ModelAnnotator
from chatGPT_data_augmentation import chatGPT_data_augmentation
from tqdm import tqdm
from typing import List, Tuple, Dict
import pandas as pd
import time
import os

class ABSAAnnotationTask:
    def __init__(self, annotator, api_key=None, pause_time=None):
        self.prompt_prefix = '''Extract each aspect term as well as associated opinion term and sentiment polarity in bullet format for comment:\n"""\n'''
        self.prompt_suffix = '''\n"""'''

        self.annotator = ModelAnnotator.create_annotator(self.prompt_prefix, self.prompt_suffix, annotator)
        self.annotator.set_api_key(api_key)
        self.annotator.set_pause_time(pause_time)

    def annotate_csv(self, path: str, column: str = "content", parse_raw_result=True):
        df = pd.read_csv(path)
        contents = df[column].tolist()
        partial_filename = path.rsplit(".")[0]
        output_path = partial_filename + f".anno_{self.annotator.annotator_name.lower()}.csv"
        results = self.annotate(contents, output_path, parse_raw_result)
        return results


    def annotate_df(self, path: str, column: str = "content", parse_raw_result=True):
        df = self.get_df(path)
        contents = df[column].tolist()
        partial_filename = path.rsplit(".")[0]
        output_path = partial_filename + f".anno_{self.annotator.annotator_name.lower()}.csv"
        results = self.annotate(contents, output_path, parse_raw_result)
        return results


    def get_df(cls, input_path, sheet_name=None)->pd.DataFrame:
        if type(input_path) == pd.DataFrame:
            return input_path
        if input_path.endswith("xlsx"):
            df = pd.read_excel(input_path, sheet_name=sheet_name)
            if type(df) == dict:
                df = list(df.values())[0]
        elif input_path.endswith("csv"):
            df = pd.read_csv(input_path)
        elif input_path.endswith("tsv"):
            df = pd.read_csv(input_path,sep='\t')
        else:
            raise Exception

        return df

    def annotate(self, contents: List[str], output_path=None, parse_raw_result=True):
        df = None
        if output_path is not None and os.path.exists(output_path):
            df = pd.read_csv(output_path)
            raw_annotation_results = df["raw_annotation_result"]

        if df is None:
            df = pd.DataFrame()
            df["content"] = contents

            raw_annotation_results = []
            for idx, content in tqdm(enumerate(contents), total=len(contents)):
                raw_annotation_result = self.annotator.annotate(content)
                raw_annotation_results.append(raw_annotation_result)
            df["raw_annotation_result"] = raw_annotation_results

            if output_path is not None:
                df.to_csv(output_path)
        if parse_raw_result:
            triplets_list = []
            for raw_annotation_result in raw_annotation_results:
                triplets = self.parse_annotation_result(raw_annotation_result)
                triplets_list.append(triplets)

            df["triplet"] = [f"{triplets}" for triplets in triplets_list]

            if output_path is not None:
                df.to_csv(output_path)

        return df

    def parse_annotation_result(self, annotation_result_raw: str) -> List[Tuple]:
        '''
        Example
        - Aspect term: gameplay
          - Opinion term: doesn't want me to play
          - Sentiment polarity: negative

        - Aspect term: game
          - Opinion term: haven't been able to experience significant gameplay
          - Sentiment polarity: negative

        - Aspect term: patch
          - Opinion term: first major patch
          - Sentiment polarity: neutral/uncertain
        :param annotation_result_raw:
        :return:
        '''
        triplets = []
        annotation_result_raw = annotation_result_raw.strip()
        for triplet_str in annotation_result_raw.split("\n\n"):
            if triplet_str.strip() == "":
                continue
            raw_kv_pairs = {
                "aspect": None,
                "opinion": None,
                "sentiment": None,
            }
            generate_triplet = False
            for line in triplet_str.split("\n"):
                line = line.strip().lstrip("-").strip().lower()
                if line == '' or 'no context or comment provided' in line or 'no aspect' in line.lower() or 'no opinion' in line.lower() \
                    or 'no sentiment' in line.lower() or 'sorry' in line.lower() or 'no other aspect' in line.lower() or 'no other opinion' in line.lower():
                    continue
                else:
                    try:
                        raw_key, value = line.split(":")[:2]
                        if raw_key == '' or value == '':
                            ''' Aspects: 
                                    creator route 
                            '''
                            continue
                        else:
                            '''Aspect term: mobile legends'''
                            for key in raw_kv_pairs.keys():
                                if 'sentiment' in key:
                                    generate_triplet = True
                                if key in line:
                                    if 'sentiment' in key:
                                        if 'neutral' in value.strip():
                                            raw_kv_pairs[key] = 'neutral'
                                        elif 'positive' in value.strip():
                                            raw_kv_pairs[key] = 'positive'
                                        elif 'negative' in value.strip():
                                            raw_kv_pairs[key] = 'negative'
                                    else:
                                        raw_kv_pairs[key] = value.strip()
                                    break
                        if generate_triplet == True:
                            triplet = (raw_kv_pairs["aspect"], raw_kv_pairs["opinion"], raw_kv_pairs["sentiment"])
                            triplets.append(triplet)
                            generate_triplet = False
                    except Exception as e:
                        print("Error: " + str(e))

        return triplets


if __name__ == "__main__":
    import argparse


    def init_args():
        parser = argparse.ArgumentParser()
        user_environment = os.environ["USER"]
        # basic settings
        parser.add_argument("--annotator", default='ChatGPT', type=str,
                            help="The name of the task, selected from: [ChatGPT, GPT3, ChatGPTWeb]")
        parser.add_argument("--input_path", default=f"/Users/{user_environment}/Desktop/Tencent_Git/test.anno_chatgpt.csv", type=str, help="")
        parser.add_argument("--column", default="content", type=str, help="")
        parser.add_argument("--api_key", default="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", type=str, help="")
        parser.add_argument("--pause_time", default=0.5, type=float, help="")
        args = parser.parse_args()

        return args


    args = init_args()
    if args.input_path.split('.')[-1] == 'csv':
        task = ABSAAnnotationTask(args.annotator, args.api_key, pause_time=args.pause_time)
        task.annotate_df(args.input_path, column=args.column, parse_raw_result=True)
    
    annotation = chatGPT_data_augmentation(args.input_path)
