import pandas as pd
import re
import json
import spacy
import string
import hashlib
from tqdm import tqdm
import os
#os.environ['KMP_DUPLICATE_LIB_OK']='True'
nlp = spacy.load(
    "en_core_web_sm", disable=["vectors", "textcat", "tagger", "parser", "ner", "lemmatizer"]
)
nlp2 = spacy.load("en_core_web_sm")

class chatGPT_data_augmentation:
    def __init__(self, input_path):
        final2_arr = []
        if input_path.split('.')[-1] == 'csv':
            df1 = pd.read_csv(input_path)
            df1.drop_duplicates(subset="content",keep="first", inplace=True)
            for index, row in tqdm(df1.iterrows(), total=df1.shape[0]):
                final2_arr = self.data_augmentation(row['content'], row['triplet'], final2_arr)
        elif input_path.split('.')[-1] == 'txt':
            with open(input_path, 'r') as f:
                for line in tqdm(f, colour="red"):
                    triplet,sentence = eval(line)
                    final2_arr = self.data_augmentation(sentence, str(triplet), final2_arr)
        
        file_path = input_path[:input_path.rfind('/')+1]
        with open(f"{file_path}/data2.json", "w") as f:
            json.dump(final2_arr, f, ensure_ascii=False, indent=4)
    
    def token_index(cls, sentence:str, aspect:str, opinion:str):
        if aspect != None and opinion != None:
            aspect = nlp(aspect)[0]
            opinion = nlp(opinion)[0]
            min_diff = float('inf')
            doc = nlp(sentence)
            aspect_index = []
            opinion_index = []
            final = []
            count = 0
            for item in doc:
                if str(aspect).strip().lower() in str(item).strip().lower():
                    aspect_index.append(count)
                
                if str(opinion).strip().lower() in str(item).strip().lower():
                    opinion_index.append(count)
                count+=1
            
            for index in opinion_index:
                for index2 in aspect_index:
                    diff = abs(index2 - index)
                    if diff < min_diff:
                        min_diff = diff
                        final = [[]]
                        final.append([index2, index])

            final = [finall for finall in final if finall != []]
        else:
            final = [[-1,-1]]
        return final

    def data_augmentation(self, sentence:str, triplets:str, final2_arr:list):
        final_dict = {}
        final_dict["sentence"] = str(sentence).strip()
        review = sentence.strip()
        clean_review = re.sub(r"(?<=[.,])(?=[^\s])", r" ", review).strip()
        doc = nlp(clean_review)
        final_dict['tokens'] = [t.text for t in doc]
        final_dict['md5_uin'] = hashlib.md5(sentence.encode()).hexdigest()
        final_dict['triplets'] = []
        for item in eval(triplets):
            final = {}
            final['aspect'] = {}
            final['opinion'] = {}
            final['aspect']['content'] = item[0]
            final['opinion']['content'] = item[1]
            final['sentiment'] = item[2]
            try:
                string_index = self.token_index(clean_review,item[0],item[1])
                if string_index == []:
                    count = 0
                    arr1 = [item[0], item[1]]
                    for items in arr1:
                        found = False
                        search_tokens = nlp(items)
                        start_index = -1
                        for i, token in enumerate(doc): # Iterate over each token in the document
                            if token.text.lower() == search_tokens[0].text.lower():  # If the current token matches the first token in the search string
                                match = True
                                for j in range(1, len(search_tokens)): # Check if the remaining tokens in the search string match the subsequent tokens in the document
                                    if i+j >= len(doc) or doc[i+j].text.lower() != search_tokens[j].text.lower():
                                        match = False
                                        break
                                if match: # If all tokens in the search string match, set the start index and exit the loop
                                    found = True
                                    start_index = i
                                    break
                        if count == 0:
                            if found == True:
                                final['aspect']['token_start'] = start_index
                                final['aspect']['token_end'] = int(start_index) + len(nlp(final['aspect']['content']))

                            else:
                                final['aspect']['token_start'] = -1
                                final['aspect']['token_end'] = -1
                        else:
                            if found == True:
                                final['opinion']['token_start'] = start_index
                                final['opinion']['token_end'] = int(start_index) + len(nlp(final['opinion']['content']))
                            else:
                                final['opinion']['token_start'] = -1
                                final['opinion']['token_end'] = -1
                        count+=1
                else:
                    if string_index[0][0] == -1:
                        final['aspect']['token_start'] = -1
                        final['aspect']['token_end'] = -1
                    else:
                        final['aspect']['token_start'] = string_index[0][0]
                        final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(final['aspect']['content']))
                    
                    if string_index[0][1] == -1:
                        final['opinion']['token_start'] = -1
                        final['opinion']['token_end'] = -1
                    else:
                        final['opinion']['token_start'] = string_index[0][1]
                        final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(final['opinion']['content']))
                if final['aspect']['token_start'] == -1 and final['opinion']['token_start'] == -1:
                    continue
                elif final['sentiment'] == None:
                    continue
                else:
                    final_dict['triplets'].append(final)
            except Exception as e:
                print(sentence)
                print("Error: " + str(e))
        final2_arr.append(final_dict)
        return final2_arr
    