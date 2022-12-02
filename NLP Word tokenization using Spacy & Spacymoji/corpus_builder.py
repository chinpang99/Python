# TO DO: 
    # Resolve all the offset prob 
    # Sentence more than 512 tokens, truncate it 

import json
import os
import re
import pandas as pd
import spacy
import nltk
from collections import defaultdict
nlp = spacy.load(
    "en_core_web_sm", disable=["vectors", "textcat", "tagger", "parser", "ner", "lemmatizer"]
)

stats = defaultdict(int)
stats["review_offset_inconsistency"] = set()
directory = "data/"

directory = '/Users/chinpangchia/Desktop/'

filtered_cols = ["标注任务ID", "md5_uin", "content", "first_relatives_result", "last_output_0"]
results = []
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

        if "I even got coco" in clean_review:
            print()

        doc = nlp(clean_review)
        #print(doc)
        # 分词 bad case
        # I'm really disappointed.the game lag very much even though I have the exact same system requirements .
        result = {}
        result["sentence"] = clean_review
        result["md5_uin"] = md5_uin
        result["task_id"] = task_id
        #result["tokens"] = [t.text for t in doc]
        result["tokens"] = nltk.word_tokenize(str(doc))[:512]
        result["triplets"] = []
        can_insert = True



        if annotation_result == {"labels": []}:
            results.append(result)
            continue
        try:
            for labels_json in annotation_result["labels"]:
                char_idx_start = labels_json["startIndex"] - NULL_LEN
                char_idx_end = labels_json["endIndex"] - NULL_LEN
                if char_idx_start < 0 and char_idx_end < 0:  # <NULL>
                    token_idx_start = token_idx_end = -1
                else:
                    if review[char_idx_start:char_idx_end] != labels_json["content"]:
                        if (review[char_idx_start:char_idx_end-1] == labels_json["content"]) or (review[char_idx_start:char_idx_end-2] == labels_json["content"]): 
                            if review[char_idx_start:char_idx_end-1] == labels_json["content"]:
                                char_idx_start-=1
                            else:
                                char_idx_start-=2
                            can_insert = True
                        elif (review[char_idx_start-1:char_idx_end] == labels_json["content"]) or review[char_idx_start-2:char_idx_end] == labels_json["content"]:
                            if review[char_idx_start-1:char_idx_end] == labels_json["content"]:
                                char_idx_start-=1
                            else:
                                char_idx_start-=2
                            can_insert = True
                        elif (review[char_idx_start-1:char_idx_end-1] == labels_json["content"]) or (review[char_idx_start-2:char_idx_end-2] == labels_json["content"]):
                            if review[char_idx_start-1:char_idx_end-1] == labels_json["content"]:
                                char_idx_start-=1;char_idx_end-=1
                            else:
                                char_idx_start-=2;char_idx_end-=2
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
            else:
                num_discard_triplets += 1
        except:
            print("some error occurs, please check....")
            import IPython

            IPython.embed()

print('#review:', len(results), '#Triplet:', sum([len(e["triplets"]) for e in results]))
print(f"num_discard_triplets:{num_discard_triplets}")
print("stats:", stats)
print(len(stats["review_offset_inconsistency"]))
with open("testing.json", "w") as f:
    json.dump(results, f, ensure_ascii=False)
