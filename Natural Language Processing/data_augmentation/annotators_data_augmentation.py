import json
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
import re
import pandas as pd
import spacy
from cleantext import clean
import numpy as np
import emoji
from collections import defaultdict
nlp = spacy.load(
    "pt_core_news_lg", disable=["vectors", "textcat", "tagger", "parser", "ner","lemmatizer"]
)

'''
Function    : Convert emoji to text
Parameters  : match object (Description: Regex Object that have ":")
Description : 1. Replace all the ":" to "< .... >"
'''
def repl(match):
    return f"<{match.group(1)}>"

def repl2(match):
    return f" {match.group(1)} "

def remove_emojis(data):
    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '  ', data)

def convert(emoji_choices:str, truncation:bool, directory:str, output_path:str):
    print("Emoji Choices: " + emoji_choices + "\nTruncation: " + str(truncation))
    stats = defaultdict(int)
    stats["review_offset_inconsistency"] = set()

    filtered_cols = ["标注任务ID", "md5_uin", "content", "first_relatives_result", "last_output_0"]
    results = []
    emoji_between_text = []
    num_discard_triplets = 0
    NULL_LEN = len("<NULL> ")
    label_filter_options = ["Yes", "No Annotation"]

    md5_uin_blacklist = {
        "a2e44015f4d9921ccd9106fbea8ddb60",
        "96ddb152e73c4174f6fd32bfe5073f36",
        "2565e1a0481f68b2fb85d46b0032220a",
        "7752ab5ffaf7cf8b0b99951430726597",
        "963995bea45539a4b57d0dd7b98ea1ce",
        "5d3db13cabf062176403cf2ed243f705",
    }

    emoji_pattern = re.compile("(.*?)["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                            "]+(.*?)", flags=re.UNICODE)

    for filename in os.listdir(directory):

        if not filename.endswith(".xlsx"):
            continue

        f = os.path.join(directory, filename)
        print(f'Processing {f}')
        df = pd.read_excel(f)

        filtered_df = df[df["last_output_0"].isin(label_filter_options)]
        filtered_df = filtered_df[filtered_cols]


        for _, entry in filtered_df.iterrows():

            content = entry["content"]
            annotation_result = entry["first_relatives_result"]
            task_id = entry["标注任务ID"]
            md5_uin = entry["md5_uin"]

            if md5_uin in md5_uin_blacklist:
                continue

            # if md5_uin == 'f826386935a45f2878a63f6a7a902d9e':
            #     print()

            review = content[NULL_LEN:].strip()
            try:
                annotation_result = json.loads(annotation_result)
            except:
                print("Json parsing error:")
                print(annotation_result)
                import IPython
                IPython.embed()
                continue

            word_id = {}
            # add space after every punctuation
            clean_review = re.sub(r"(?<=[.,])(?=[^\s])", r" ", review).strip()
            doc = nlp(clean_review)
            # 分词 bad case
            # I'm really disappointed.the game lag very much even though I have the exact same system requirements .
            result = {}
            if emoji_choices == 'text_without_emoji':
                # result["sentence"] = clean(clean_review, no_emoji=True)
                result["sentence"] = remove_emojis(clean_review)
                if truncation == True:
                    result["tokens"] = [t.text for t in doc][:512]
                    result["tokens"] = remove_emojis(result["tokens"])
                else:
                    result["tokens"] = [t.text for t in nlp(result["sentence"])]
            elif emoji_choices == 'emoji_to_text':
                result["sentence"] = re.sub("\:(.*?)\:", repl ,emoji.demojize(clean_review))
                if truncation == True:
                    result["tokens"] = [t.text for t in nlp(re.sub("\:(.*?)\:", repl2 ,emoji.demojize(clean_review)))][:512]
                else:
                    result["tokens"] = [t.text for t in nlp(re.sub("\:(.*?)\:", repl2 ,emoji.demojize(clean_review)))]
            else:
                result["sentence"] = clean_review
                if truncation == True:
                    result["tokens"] = [t.text for t in nlp(result["sentence"])][:512]
                else:
                    result["tokens"] = [t.text for t in nlp(result["sentence"])]
            result["md5_uin"] = md5_uin
            result["task_id"] = task_id
            result["triplets"] = []
            can_insert = True
            emoji_between_text_bool = False



            if annotation_result == {"labels": []}:
                results.append(result)
                continue
            try:
                #token_idx_start = token_idx_end = 0
                for labels_json in annotation_result["labels"]:
                    char_idx_start = labels_json["startIndex"] - NULL_LEN
                    char_idx_end = labels_json["endIndex"] - NULL_LEN
                    if char_idx_start < 0 and char_idx_end < 0:  # <NULL>
                        token_idx_start = token_idx_end = -1
                    else:
                        if review[char_idx_start:char_idx_end] != labels_json["content"]:
                            if (review[char_idx_start:char_idx_end-1] == labels_json["content"]) or (review[char_idx_start:char_idx_end-2] == labels_json["content"]):
                                if review[char_idx_start:char_idx_end-1] == labels_json["content"]:
                                    char_idx_end-=1
                                else:
                                    char_idx_end-=2
                                if emoji_pattern.findall(review[char_idx_start:char_idx_end]) != "": #Capture the sentence that have emoji between text
                                    emoji_between_text_bool = True
                                can_insert = True
                            elif (review[char_idx_start-1:char_idx_end] == labels_json["content"]) or review[char_idx_start-2:char_idx_end] == labels_json["content"]:
                                if review[char_idx_start-1:char_idx_end] == labels_json["content"]:
                                    char_idx_start-=1
                                else:
                                    char_idx_start-=2
                                if emoji_pattern.findall(review[char_idx_start:char_idx_end]) != "": #Capture the sentence that have emoji between text
                                    emoji_between_text_bool = True
                                can_insert = True
                            elif (review[char_idx_start-1:char_idx_end-1] == labels_json["content"]) or (review[char_idx_start-2:char_idx_end-2] == labels_json["content"]):
                                if review[char_idx_start-1:char_idx_end-1] == labels_json["content"]:
                                    char_idx_start-=1;char_idx_end-=1
                                else:
                                    char_idx_start-=2;char_idx_end-=2
                                if emoji_pattern.findall(review[char_idx_start:char_idx_end]) != "":
                                    emoji_between_text_bool = True
                                can_insert = True
                            elif review[char_idx_start:char_idx_end+1] == labels_json["content"] or review[char_idx_start:char_idx_end+2] == labels_json["content"]:
                                if review[char_idx_start:char_idx_end+1] == labels_json["content"]:
                                    char_idx_end+=1
                                else:
                                    char_idx_end+=2
                                if emoji_pattern.findall(review[char_idx_start:char_idx_end]) != "": #Capture the sentence that have emoji between text
                                    emoji_between_text_bool = True
                                can_insert = True
                            elif review[char_idx_start+1:char_idx_end] == labels_json["content"] or review[char_idx_start+2:char_idx_end] == labels_json["content"]:
                                if review[char_idx_start+1:char_idx_end] == labels_json["content"]:
                                    char_idx_start+=1
                                else:
                                    char_idx_start+=2
                                if emoji_pattern.findall(review[char_idx_start:char_idx_end]) != "": #Capture the sentence that have emoji between text
                                    emoji_between_text_bool = True
                                can_insert = True
                            elif review[char_idx_start+1:char_idx_end+1] == labels_json["content"] or review[char_idx_start+2:char_idx_end+2] == labels_json["content"]:
                                if review[char_idx_start+1:char_idx_end+1] == labels_json["content"]:
                                    char_idx_start+=1;char_idx_end+=1
                                else:
                                    char_idx_start+=2;char_idx_end+=2
                                if emoji_pattern.findall(review[char_idx_start:char_idx_end]) != "": #Capture the sentence that have emoji between text
                                    emoji_between_text_bool = True
                                can_insert = True
                            else:
                                print(
                                    f'{review[char_idx_start:char_idx_end]} must equal to {labels_json["content"]}'
                                )
                                stats["triplet_offset_inconsistency"] += 1
                                stats["review_offset_inconsistency"].add(md5_uin)
                                can_insert = False
                        # TODO: check if there is some annotation breaks it, and figure out how to resolve it
                        try:
                            span = doc.char_span(char_idx_start, char_idx_end)
                            if span is None: #fix subword
                                for t in doc:
                                    l, r = t.idx, t.idx + len(t.text)
                                    if l <= char_idx_start <= r:
                                        char_idx_start = l

                                    if l <= char_idx_end <= r:
                                        char_idx_end = r

                                if char_idx_end >= len(review):
                                    char_idx_end = len(review)

                                span = doc.char_span(char_idx_start, char_idx_end)

                            # if span is not None:
                            #     can_insert = True

                            token_idx_start, token_idx_end = span.start, span.end
                            labels_json["content"] = review[char_idx_start:char_idx_end]
                        except AttributeError as e:
                            # idx mismatch
                            print(e)
                            current_char_cnt = 0
                            for idx, token in enumerate(result["tokens"]):
                                if (
                                    char_idx_start < current_char_cnt
                                    or current_char_cnt > char_idx_end
                                ):
                                    continue
                                if labels_json["content"].startswith(token):
                                    token_idx_start = idx
                                if labels_json["content"].endswith(token):
                                    token_idx_end = idx + 1
                                current_char_cnt += len(token)
                    if token_idx_start>token_idx_end:
                        can_insert = False
                    word_id[labels_json["id"]] = {
                        "content": labels_json["content"],
                        "token_start": token_idx_start,
                        "token_end": token_idx_end,
                    }

                for connection in annotation_result["connections"]:
                    from_id = connection["fromId"]
                    to_id = connection["toId"]
                    start_word = word_id[from_id]
                    triplet = {}
                    triplet["opinion"] = word_id[from_id]
                    triplet["aspect"] = word_id[to_id]
                    triplet["sentiment"] = connection.get("tag", "Missing") # connection["tag"]
                    result["triplets"].append(triplet)
                if can_insert:
                    results.append(result)
                    if emoji_between_text_bool:
                        emoji_between_text.append(result)
                else:
                    num_discard_triplets += 1
            except Exception as e:
                print(e)
                print("some error occurs, please check....")
                import IPython

                IPython.embed()

    print('#review:', len(results), '#Triplet:', sum([len(e["triplets"]) for e in results]))
    print(f"num_discard_triplets:{num_discard_triplets}")
    print("stats:", stats)
    print(len(stats["review_offset_inconsistency"]))
    #with open("../data/absa_data_20221125.json", "w") as f:
    os.chdir(output_path)
    with open("result.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    with open("emoji_between_text.json", "w") as f: #A Json file that stored the sentences of emoji between text
        json.dump(emoji_between_text, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    user_environment = os.environ["USER"]
    #basic settings
    parser.add_argument(
        "--emoji_choices",
        default="text_with_emoji",
        required=False,
        type=str,
        choices=['text_with_emoji', 'emoji_to_text', 'text_without_emoji'],
        help="The choices either 'text_with_emoji', 'emoji_to_text' or 'text_without_emoji'"
    )
    parser.add_argument(
        "--truncation",
        required=False,
        action='store_true',
        help="A boolean either 'True' or 'False'"
    )
    parser.add_argument(
        "--input_path",
        default="/Users/{user_environment}/Library/Containers/com.tencent.WeWorkMac/Data/WeDrive/腾讯/NLP-Task-Data/等待验收/Aspect Sentiment/ABSA PT HOK/Weekly ABSA Generation/20.04".format(user_environment = user_environment),
        required=False,
        type=str,
        help="Insert input path"
    )
    parser.add_argument(
        "--output_path",
        default="/Users/{user_environment}/Downloads".format(user_environment = user_environment),
        required=False,
        type=str,
        help="Insert result output path"
    )
    args = parser.parse_args()
    emoji_choices = args.emoji_choices
    truncation = args.truncation
    input_path = args.input_path
    output_path = args.output_path
    convert(emoji_choices, truncation, input_path, output_path)