import argparse
import os
from typing import List, Dict
import json
import random
from regexcollection import SocialMediaRegex
from absa_format_converter import ABSAFormatConvert
from tabulate import tabulate
import datetime

def concatList(old_data_input_path:str):
    os.chdir(old_data_input_path)
    #content_list = []
    final = []
    final_set = {}

    for line in open("test.txt",encoding='utf-8'):
        line = line.strip()
        line = eval(line)
        final.append(line['md5_uin'])
    
    for line in open("train.txt",encoding='utf-8'):
        line = line.strip()
        line = eval(line)
        final.append(line['md5_uin'])
    
    for line in open("valid.txt",encoding='utf-8'):
        line = line.strip()
        line = eval(line)
        final.append(line['md5_uin'])
           
    final_set = set(final)
    return final_set

def checkDuplicate(filePath:str, result:str):
    final = []
    all_data : List = json.load(open(filePath))
    for item in all_data:
        try:
            if item['md5_uin'] in result:
                print("Found")
            else:
                final.append(item)
        except:
            continue
    return final

def stat(data, return_str=False):
    if type(data) == str:
        data = open(data).readlines()
        data = [json.loads(entry.rstrip()) for entry in data]


    stats = {
        '#review': len(data),
        "#triplet":0,
        "#pair":0,
        "#aspect_term":0,
        "#opinion_term":0,
        'review_avg_token':0,
        'review_max_token': 0,
        'review_min_token': 100000,
    }


    for entry in data:
        tokens = entry['tokens']
        stats['review_avg_token'] += len(tokens)

        if stats['review_max_token'] < len(tokens):
            stats['review_max_token'] = len(tokens)

        if stats['review_min_token'] > len(tokens):
            stats['review_min_token'] = len(tokens)


        sent = ' '.join(tokens)

        for triplet in entry['triplets']:
            opinion = triplet['opinion']
            aspect = triplet['aspect']


            if 'content' in aspect and 'content' in opinion and 'sentiment' in triplet:
                s = triplet['sentiment']
                o = opinion['content']
                a = aspect['content']

            a = SocialMediaRegex.replace_nonascii(a, replace_nonascii2space=False, replace_french_letter=False,
                                                  replace_nonenpunc_letter=True)
            o = SocialMediaRegex.replace_nonascii(o, replace_nonascii2space=False, replace_french_letter=False,
                                                  replace_nonenpunc_letter=True)

            if a != '<NULL>':
                stats["#aspect_term"] += 1

            if o != '<NULL>':
                stats["#opinion_term"] += 1

            if a != '<NULL>' and o != '<NULL>':
                stats["#pair"] += 1

                if s != "":
                    stats["#triplet"] += 1
    if data:
        stats['review_avg_token'] = stats['review_avg_token'] // len(data)
    else:
        stats['review_avg_token'] = 0
    
    if return_str:
        table = [[k, v] for k, v in stats.items()]
        return tabulate(table)
    else:
        return stats

sentiment_map = {
    "Neutral": "Neutral",
    "Positive": "Positive",
    "positive": "Positive",
    "Negative": "Negative",
    "negative": "Negative",
    "Conflict": "Neutral",
    "Missing": "Neutral",
}
NULL = "<NULL>"

def fix_term(term:Dict):
    boundary = term["token_start"], term["token_end"]
    token_start, token_end = min(boundary), max(boundary)
    if (token_start == -1 and token_end >= 0) or (token_end == -1 and token_start >= 0):
        # import IPython
        # IPython.embed()
        raise Exception

    if token_start == token_end == -1:
        term["content"] = NULL
    else:
        pass

    term["token_start"] = token_start
    term["token_end"] = token_end


def fix_data(datas: List) -> List:
    for data in datas:
        triplets = []
        for triplet in data["triplets"]:

            try:
                fix_term(triplet["aspect"])
                fix_term(triplet["opinion"])
            except:
                print(triplet)
            
            
            try:
                triplet["sentiment"] = sentiment_map[triplet["sentiment"]]
            except:
                continue
            
            if triplet['aspect'] == {} or triplet['aspect'] == '' or 'sentiment' not in triplet or 'content' not in triplet:
                continue
            else:
                if triplet["aspect"]["content"] == NULL and triplet["opinion"]["content"] == NULL:
                    continue
                
                triplets.append(triplet)

            data["triplets"] = triplets

    return datas

def create_dataset(dataset_path, version, output_dir = None, ratio = None, random_seed=9997):
    print(output_dir)
    random.seed(random_seed)
    all_data : List = dataset_path
    all_data = fix_data(all_data)
    random.shuffle(all_data)



    if ratio is None:
        ratio = {
            'train':0.8,
            'valid':0.1,
            'test':0.1,
        }


    dataset = {}
    size = len(all_data)
    start = 0
    for idx, split_name in enumerate(ratio.keys()):
        if idx < len(ratio) - 1:
            l = int(size * ratio[split_name])
            dataset[split_name] = all_data[start:start+l]
            start += l
        else:
            dataset[split_name] = all_data[start:size]
            start = len(all_data)



    if output_dir is not None:
        output_dir = output_dir + f"_{version}"
        os.makedirs(output_dir, exist_ok=True)

        with open(os.path.join(output_dir, 'dataset.log'), 'w') as flog:
            now = datetime.datetime.now()
            flog.write(f'Created on {now} with ratio: {ratio}\n')

            split_name = "all"
            print(f'{split_name}:', file=flog)
            print(stat(all_data, return_str=True), file=flog)
            print(file=flog)


            for split_name, split_data in dataset.items():
                output_path = os.path.join(output_dir, f'{split_name}.txt')
                with open(output_path, "w") as fout:
                    for entry in split_data:
                        fout.write(json.dumps(entry, ensure_ascii=False) + '\n')

                print(f'{split_name}:')
                print(stat(split_data, return_str=True))
                print()

                print(f'{split_name}:', file=flog)
                print(stat(split_data, return_str=True), file=flog)
                print(file=flog)
    return dataset

def generate_output(old_data_input_path:str, new_data_input_path:str, version:str):
    files = ['train', 'test', 'valid']
    for file in files:
        data = data2 = "" 
        if old_data_input_path != "":
            os.chdir(old_data_input_path)
            with open(f'{file}.txt') as fp: 
                data = fp.read() 
        
        os.chdir(f'{new_data_input_path}_{version}')
        with open(f'{file}.txt') as fp: 
            data2 = fp.read() 
        data += data2 
        with open (f'{file}.txt', 'w') as fp: 
            fp.write(data)

def convert(new_data_input_path:str,old_data_input_path:str,data_output_path:str, version:str, toFormat:str, splits: str, ratio):
    if old_data_input_path != "":
        md5_list = concatList(old_data_input_path)
    else:
        md5_list = {}
    unique_data_list = checkDuplicate(new_data_input_path, md5_list)
    create_dataset(unique_data_list, ratio=ratio, version=version, output_dir=data_output_path)
    generate_output(old_data_input_path, data_output_path,version)
    converted = ABSAFormatConvert(from_format='game', to_format=toFormat)

    converted.convert_splits(
        version=version,
        dataset_dir=data_output_path,
        splits=splits.split(","),
    )


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    # user_environment = os.environ["USER"]
    parser.add_argument(
        "--new_data_input_path",
        default="/Users/chinpangchia/Desktop/Python/automation_pipeline/result.json",
        required=False,
        type=str,
        help="Insert data input path"
    )
    parser.add_argument(
        "--old_data_input_path",
        default="",
        required=False,
        type=str,
        help="Insert data input path"
    )
    parser.add_argument(
        "--data_output_path",
        default="/Users/chinpangchia/Desktop/Tencent_Git/data_augmentation/game_gas_format_file_creation_process/game",
        required=False,
        type=str,
        help="Insert data output path"
    )
    parser.add_argument(
        "--version",
        default=1,
        required=False,
        type=str,
        help="Insert data version"
    )
    parser.add_argument(
        "--train",
        default=1,
        required=False,
        type=str,
        help="Insert data splitting ratio"
    )
    parser.add_argument(
        "--valid",
        default=0,
        required=False,
        type=str,
        help="Insert data splitting ratio"
    )
    parser.add_argument(
        "--test",
        default=0,
        required=False,
        type=str,
        help="Insert data splitting ratio"
    )
    parser.add_argument(
        "--to_format",
        default='gas', 
        type=str, 
        required=False,
        help="The name of the task, selected from: [game, gas, quad]"
    )
    parser.add_argument(
        "--splits"
        , default="train,valid,test"
        , type=str
    )
    args = parser.parse_args()
    new_data_input_path = args.new_data_input_path
    old_data_input_path = args.old_data_input_path 
    data_output_path = args.data_output_path
    data_version = args.version
    to_format = args.to_format # gas
    splits = args.splits
    ratio = {
        'train': args.train,
        'valid': args.valid,
        'test': args.test,
    }

    convert(new_data_input_path,old_data_input_path,data_output_path, data_version, to_format, splits, ratio)
