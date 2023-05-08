import pandas as pd
import re
import json
import spacy
import string
import hashlib
nlp = spacy.load(
    "en_core_web_sm", disable=["vectors", "textcat", "tagger", "parser", "ner", "lemmatizer"]
)

def isFloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def textRemoveNumbersAndSymbols(string:str):
    result = "".join(filter(lambda x: not x.isdigit(), string))
    result = re.sub(r'[^\w]', ' ', result)
    return result

def textRemoveSymbols(sentence:str):
    result = sentence
    for punctuation in string.punctuation:
        result = result.replace(punctuation, " ")
    
    for result2 in result.split(" "):
        if result2 != "":
            return result2


def extract_aspect_opinion(sentence:str, aspect_term:str, opinion_term:str):
  aspect_start = sentence.index(aspect_term)
  opinion_start = sentence.index(opinion_term)
  aspect_opinion = sentence[aspect_start:opinion_start]
  return aspect_opinion

def check_sentiment_follows_aspect(sentence, opinion_term):
  opinion_start = sentence.index(opinion_term)
  if "sentiment: " in sentence[opinion_start:]:
    return True
  else:
    return False

def check_sentiment(string:str):
    # Split the string into a list of substrings using the comma as the delimiter
    substrings = string.split(',')
    # Get the last element of the list (i.e. the substring after the last comma)
    last_substring = substrings[-1]
    # Strip leading and trailing whitespace from the substring
    last_substring = last_substring.strip()
    if "sentiment:" in last_substring:
      return True
    else:
      return False

def keys_definition(string:str):
    if "aspect" in string.strip().lower():
        return "aspect"
    elif "opinion" in string.strip().lower():
        return "opinion"
    elif "sentiment" in string.strip().lower():
        return "sentiment"
    elif "confidence" in string.strip().lower():
        return "confidence"

def testing(sentence:str, aspect:str, opinion:str):
    if aspect != None and opinion != None:
        aspect = nlp(aspect)[0]
        opinion = nlp(opinion)[0]
        min_diff = float('inf')
        doc = nlp(sentence[NULL_LEN:])
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


if __name__ == "__main__":
    df1 = pd.read_excel(r'/Users/chinpangchia/Desktop/Python/ChatGPT_GPT3/GPT3_final_result.xlsx')

    final_arr = []
    final2_arr = []
    NULL_LEN = len("<NULL> ")

    for index, row in df1.iterrows():
        final_dict = {}
        content = row['content:string']
        final_dict["sentence"] = content[NULL_LEN:].strip()
        review = content[NULL_LEN:].strip()
        clean_review = re.sub(r"(?<=[.,])(?=[^\s])", r" ", review).strip()
        doc = nlp(clean_review)
        final_dict['tokens'] = [t.text for t in doc]
        final_dict['md5_uin'] = hashlib.md5(row['content:string'].encode()).hexdigest()
        final_dict['task_id'] = 10000
        final_dict['triplets'] = []
        if "[" in row['result_raw'] and "{" in row['result_raw']: #Json Format
            try:
                item = eval(row['result_raw'])
                for item2 in item:
                    final = {}
                    final['aspect'] = {}
                    final['opinion'] = {}
                    if "aspect_term" in item2:
                        final['aspect']['content'] = item2['aspect_term']
                        final['opinion']['content'] = item2['opinion_term']
                        string_index = testing(row["content:string"],textRemoveSymbols(item2['aspect_term']),textRemoveSymbols(item2['opinion_term']))
                        if string_index != []:
                            final['aspect']['token_start'] = string_index[0][0]
                            final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(item2['aspect_term']))
                            final['opinion']['token_start'] = string_index[0][1]
                            final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(item2['opinion_term']))
                        final['sentiment'] = item2['sentiment']
                        final['confidence'] = item2['confidence_score']
                    elif "confidence" not in item2:
                        final['aspect']['content'] = item2['aspect']
                        final['opinion']['content'] = item2['opinion']
                        string_index = testing(row["content:string"],textRemoveSymbols(item2['aspect']),textRemoveSymbols(item2['opinion']))
                        if string_index != []:
                            final['aspect']['token_start'] = string_index[0][0]
                            final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(item2['aspect']))
                            final['opinion']['token_start'] = string_index[0][1]
                            final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(item2['opinion']))
                        final['sentiment'] = item2['sentiment']
                    else:
                        final['aspect']['content'] = item2['aspect']
                        final['opinion']['content'] = item2['opinion']
                        string_index = testing(row["content:string"],textRemoveSymbols(item2['aspect']),textRemoveSymbols(item2['opinion']))
                        if string_index != []:
                            final['aspect']['token_start'] = string_index[0][0]
                            final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(item2['aspect']))
                            final['opinion']['token_start'] = string_index[0][1]
                            final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(item2['opinion']))
                        final['sentiment'] = item2['sentiment']
                        final['confidence'] = item2['confidence']
                    final_dict['triplets'].append(final)
            except Exception as e: #Invalid JSON Format
                continue
        elif "[" in row['result_raw'] and "(" in row['result_raw']: #Dictionary format
            try:
                for item in eval(row['result_raw']):
                    result_dict = {}
                    result_dict['aspect'] = {}
                    result_dict['opinion'] = {}
                    result_dict['aspect']['content'] = item[0]
                    result_dict['opinion']['content'] = item[1]
                    string_index = testing(row["content:string"],textRemoveSymbols(item[0]),textRemoveSymbols(item[1]))
                    if string_index != []:
                        result_dict['aspect']['token_start'] = string_index[0][0]
                        result_dict['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(item[0]))
                        result_dict['opinion']['token_start'] = string_index[0][1]
                        result_dict['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(item[1]))
                    result_dict['sentiment'] = item[2]
                    result_dict['confidence'] = item[3]
                    final_dict['triplets'].append(result_dict)
            except Exception as e: #No Aspect or Opinion term
                continue            
        elif "[" in row['result_raw']: 
            '''[aspect_term: released in a worse state, opinion_term: beyond my comprehension, sentiment: negative, confidence: 0.8], '''
            #print(row["content:string"])
            if "aspect_term" in row['result_raw']:
                row["result_raw"] = row["result_raw"].replace("],", "")
                for item in row['result_raw'].split("["):
                    final = {}
                    final['aspect'] = {}
                    final['opinion'] = {}
                    if item == "\n\n" or item == "" or item == " ":
                        continue
                    else:
                        for item2 in item.split(","):
                            key,value = item2.split(":")
                            key = keys_definition(key)
                            if key == 'aspect' or key == 'opinion':
                                final[key]['content'] = value.strip()
                            else:
                                final[key] = value.strip()
                    string_index = testing(row["content:string"],textRemoveSymbols(final['aspect']['content']),textRemoveSymbols(final['opinion']['content']))
                    if string_index != []:
                        final['aspect']['token_start'] = string_index[0][0]
                        final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(final['aspect']['content']))
                        final['opinion']['token_start'] = string_index[0][1]
                        final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(final['opinion']['content']))
                    final_dict['triplets'].append(final)
            elif "Aspect Term" in row['result_raw']:
                diffFormat = False
                #print(row["content:string"])
                final = {}
                final['aspect'] = {}
                final['opinion'] = {}
                for item in row['result_raw'].split("\n"):
                    item = item.replace("[", "")
                    item = item.replace("],", "")
                    item = item.replace("]", "")
                    if item == "" or item == " ":
                        continue
                    elif "Opinion Term" in item and "Sentiment" in item: 
                        '''[Aspect Term: Game, Opinion Term: Enjoy, Sentiment: Positive, Confidence Score: 0.8], '''
                        final = {}
                        final['aspect'] = {}
                        final['opinion'] = {}
                        for item2 in item.split(","):
                            key, value = item2.split(":")
                            key = keys_definition(key)
                            if key == 'aspect' or key == 'opinion':
                                final[key]['content'] = value.strip()
                            else:
                                final[key] = value.strip()
                        string_index = testing(row["content:string"],textRemoveSymbols(final['aspect']['content']),textRemoveSymbols(final['opinion']['content']))
                        if string_index != []:
                            final['aspect']['token_start'] = string_index[0][0]
                            final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(final['aspect']['content']))
                            final['opinion']['token_start'] = string_index[0][1]
                            final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(final['opinion']['content']))
                        final_dict['triplets'].append(final)
                        diffFormat = True
                    else: 
                        '''Aspect Term: Competitive nature, FPS shooters, Left 4 Dead, Darktide, coop game, multiplayer games, Vermintide, Tomes and Grimores'''
                        key,value = item.split(":")
                        key = keys_definition(key)
                        if key == 'aspect' or key == 'opinion':
                            final[key]['content'] = value.strip()
                        else:
                            final[key] = value.strip()
                        final.pop('user feedback', None)
                if diffFormat == False:
                    string_index = testing(row["content:string"],textRemoveSymbols(final['aspect']['content']),textRemoveSymbols(final['opinion']['content']))
                    if string_index != []:
                        final['aspect']['token_start'] = string_index[0][0]
                        final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(final['aspect']['content']))
                        final['opinion']['token_start'] = string_index[0][1]
                        final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(final['opinion']['content']))
                    final_dict['triplets'].append(final)
        elif "No list can be extracted" in row['result_raw'] or "sentence does not contain any" in row["result_raw"] or row["result_raw"] == "#ERROR" \
        or "positive opinion term" in row["result_raw"].strip() or "negative opinion term" in row["result_raw"].strip() or "positive: opinion term" in row["result_raw"].strip() \
            or "negative: opinion term" in row["result_raw"].strip() or "opinion term: low, sentiment:" in row['result_raw'].strip() or "opinion term: high, sentiment:,"in row['result_raw'].strip():
            continue
        elif "1. Aspect Term:" in row["result_raw"] and "2. Opinion Term:"in row["result_raw"]and "3. Sentiment:"in row["result_raw"]and "4. Confidence Score"in row["result_raw"]:
            '''
                1. Aspect Term: Gameplay, Performance, Shaders, Cash Shop, Crafting, Weapon Mods, Weapons, Subclasses, Scoreboard, Post Match Replay Button, Features, Quality of Life
                2. Opinion Term: Super Fun, Trash, Worse, Missing, Incomplete
                3. Sentiment: Positive, Negative
                4. Confidence Score: 0.9, 0.8, 0.7, 0.6, 0.5
            '''
            final = {}
            final['aspect'] = {}
            final['opinion'] = {}
            for item in row["result_raw"].split("\n"):
                if "Aspect Term" in item:
                    final["aspect"]['content'] = item.split(":",1)[1]
                elif "Opinion Term" in item:
                    final["opinion"]['content'] = item.split(":",1)[1]
                elif "Sentiment" in item:
                    final["sentiment"] = item.split(":",1)[1]
                elif "Confidence Score" in item:
                    final["confidence"] = item.split(":",1)[1]
            string_index = testing(row["content:string"],textRemoveSymbols(final['aspect']['content']),textRemoveSymbols(final['opinion']['content']))
            if string_index != []:
                final['aspect']['token_start'] = string_index[0][0]
                final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(final['aspect']['content']))
                final['opinion']['token_start'] = string_index[0][1]
                final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(final['opinion']['content']))
            final_dict["triplets"].append(final)
        else:
            for result in row['result_raw'].split('\n'):
                if result == '':
                    continue
                
                elif result[0].isdigit(): #and "aspect" in str(row['result_raw']).strip().lower():
                    result_dict = {}
                    #print(row['content:string'])
                    if "|" in result:
                        if "aspect" in result.lower() and "opinion" in result.lower() and "sentiment" in result.lower():
                            for result2 in result.split("|"):
                                if ":" in result2:
                                    key, value = result2.split(":")
                                    res = "".join(filter(lambda x: not x.isdigit(), key))
                                    res = re.sub(r'[^\w]', ' ', res)
                                    if 'aspect term' in res.strip().lower():
                                        result_dict['aspect'] = value.strip()
                                    elif 'opinion term' in res.strip().lower():
                                        result_dict['opinion'] = value.strip()
                                    else:
                                        result_dict[res.strip().lower()] = value.strip()
                        elif result.count("|") == 3:
                            if "." in result.split("|")[0]:
                                '''1. Game | Fun | Positive | 0.8'''
                                result_dict['aspect'] = (result.split("|")[0]).split(".",1)[1]
                                result_dict['opinion'] = result.split("|")[1]
                                result_dict['sentiment'] = result.split("|")[2]
                                result_dict['confidence score'] = result.split("|")[3]
                            else:
                                '''Rough around the edges | NULL | Negative | 0.8'''
                                result_dict['aspect'] = result.split("|")[0]
                                result_dict['opinion'] = result.split("|")[1]
                                result_dict['sentiment'] = result.split("|")[2]
                                result_dict['confidence score'] = result.split("|")[3]
                        if len(result_dict) >0:
                            if "," in result_dict['aspect']:
                                for result2 in result_dict['aspect'].split(","):
                                    final3 = {}
                                    final3['aspect'] = {}
                                    final3["opinion"] = {}
                                    final3["aspect"]['content'] = result2.strip()
                                    final3["opinion"]['content'] = result_dict['opinion']
                                    final3["sentiment"] = result_dict['sentiment']
                                    if "confidence score" in result_dict:
                                        final3["confidence"] = result_dict['confidence score']
                                    else:
                                        final3["confidence"] = result_dict['confidence']
                                    string_index = testing(row["content:string"],textRemoveSymbols(final3['aspect']['content']),textRemoveSymbols(final3['opinion']['content']))
                                    if string_index != []:
                                        final3['aspect']['token_start'] = string_index[0][0]
                                        final3['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(final3['aspect']['content']))
                                        final3['opinion']['token_start'] = string_index[0][1]
                                        final3['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(final3['opinion']['content']))
                                    final_dict['triplets'].append(final3)
                            else:
                                final = {}
                                final['aspect'] = {}
                                final["opinion"] = {}
                                final['aspect']['content'] = result_dict['aspect']
                                final['opinion']['content'] = result_dict['opinion']
                                final['sentiment'] = result_dict['sentiment']
                                if "confidence score" in result_dict:
                                    final["confidence"] = result_dict['confidence score']
                                else:
                                    final["confidence"] = result_dict['confidence']
                                string_index = testing(row["content:string"],textRemoveSymbols(final['aspect']['content']),textRemoveSymbols(final['opinion']['content']))
                                if string_index != []:
                                    final['aspect']['token_start'] = string_index[0][0]
                                    final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(final['aspect']['content']))
                                    final['opinion']['token_start'] = string_index[0][1]
                                    final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(final['opinion']['content']))
                                final_dict['triplets'].append(final)
                    elif "(aspect term):" in result.strip().lower(): #Ignore because invalid format => 1. Gunplay (aspect term): nice (opinion term): fun (sentiment): positive (confidence score): 0.9
                        final_dict.clear()
                        continue
                    elif result.count("=") == 4:
                        '''1. Game: aspect=state, opinion=broken, sentiment=negative, confidence=0.9'''
                        semicolon_index = result.index(":")
                        item = result[semicolon_index + 1:]
                        final = {}
                        final['aspect'] = {}
                        final["opinion"] = {}
                        for item2 in item.split(","):
                            key, value = item2.split("=")
                            key = keys_definition(key)
                            if key == 'aspect' or key == 'opinion':
                                final[key]['content'] = value.strip()
                            else:
                                final[key.strip().lower()] = value.strip()
                        string_index = testing(row["content:string"],textRemoveSymbols(final['aspect']['content']),textRemoveSymbols(final['opinion']['content']))
                        if string_index != []:
                            final['aspect']['token_start'] = string_index[0][0]
                            final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(final['aspect']['content']))
                            final['opinion']['token_start'] = string_index[0][1]
                            final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(final['opinion']['content']))
                        final_dict["triplets"].append(final)
                    elif result.count(":") == 3:
                        #print(row["content:string"])
                        final = {}
                        final['aspect'] = {}
                        final['opinion'] = {}
                        if "aspect term" in result.strip() and result.count("aspect") == 1 and result.count("opinion") == 1 and result.count("sentiment") == 1:
                            '''1. Combat: aspect term, fantastic: opinion term, positive: sentiment, 0.9'''
                            for item in result.split(","):
                                if isFloat(item):
                                    final['confidence'] = item
                                else:
                                    value, key = item.split(":")
                                    key = keys_definition(key)
                                    if "sentiment" in key:
                                        '''1. System: aspect term, hit min spec: opinion term, 0.8: sentiment, confidence score'''
                                        if isFloat(value):
                                            final = {}
                                            break
                                        else:
                                            if key == 'aspect' or key == 'opinion':
                                                final[key]['content'] = value.strip()
                                            else:
                                                final[key.strip().lower()] = value.strip()
                                    else:
                                        if "aspect term" in key:
                                            value = value.split(".",1)[1]
                                        if key == 'aspect' or key == 'opinion':
                                            final[key]['content'] = value.strip()
                                        else:
                                            final[key.strip().lower()] = value.strip()
                                
                        elif "aspect term" in result.strip() and (result.count("aspect") > 1 or result.count("opinion") > 1 ):
                            '''2. public bug tracker: aspect term, serious bugs: aspect term, known issues: opinion term, negative sentiment, 0.9 confidence score'''
                            aspect_arr = []
                            opinion_arr = []
                            # if result.count('aspect term') > 1:
                            for item in result.split(","):
                                if "aspect term" in item.strip().lower():
                                    aspect_arr.append(textRemoveNumbersAndSymbols(item.split(":")[0]))
                                    final['aspect']['content'] = ",".join(aspect_arr)
                                elif "opinion term" in item.strip().lower():
                                    opinion_arr.append(textRemoveNumbersAndSymbols(item.split(":")[0]))
                                    final['opinion']['content'] = ",".join(opinion_arr)
                                elif "sentiment" in item.strip().lower():
                                    final['sentiment'] = item.strip().split(" ")[0]
                                elif "confidence score" in item.strip().lower():
                                    final['confidence'] = item.strip().split(" ")[0]
                        else:
                            '''1. duty: end: positive: 0.8'''
                            final['aspect']['content'] = textRemoveNumbersAndSymbols(result.split(":")[0])
                            final['opinion']['content'] = result.split(":")[1]
                            final['sentiment'] = result.split(":")[2]
                            final['confidence'] = result.split(":")[3]
                        
                        if final != {}:
                            string_index = testing(row["content:string"],textRemoveSymbols(final['aspect']['content']),textRemoveSymbols(final['opinion']['content']))
                            if string_index != []:
                                final['aspect']['token_start'] = string_index[0][0]
                                final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(final['aspect']['content']))
                                final['opinion']['token_start'] = string_index[0][1]
                                final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(final['opinion']['content']))
                            final_dict["triplets"].append(final)
                    elif result.count("-") == 4 and ":" in result:
                        #print(row["content:string"])
                        final = {}
                        final['aspect'] = {}
                        final['opinion'] = {}
                        '''1. Group 1: Aspect - Gameplay Loop Devs, Opinion - Real Reason for Fun, Sentiment - Positive, Confidence - 1'''
                        item = result.split(":",1)[1]
                        if item.count(",") > 3:
                            '''12. Gameplay itself: aspect term- gameplay itself, opinion term- fun, barring the chip damage, sentiment- positive, confidence score- 0.8'''
                            aspect_term = extract_aspect_opinion(item.strip().lower(), "aspect", "opinion")
                            opinion_term = extract_aspect_opinion(item.strip().lower(), "opinion", "sentiment")
                            sentiment = extract_aspect_opinion(item.strip().lower(), "sentiment", "confidence")

                            final['aspect']['content'] = aspect_term.split("-",1)[1].replace(",", "")
                            final['opinion']['content'] = opinion_term.split("-",1)[1].replace(",", "")
                            final['sentiment'] = sentiment.split("-",1)[1].replace(",", "")
                        elif item.count(";") == 3:
                            '''1. Fat Shark: aspect term - released an incomplete, broken game; opinion term - scummy monetization schemes; sentiment - negative; confidence score - 0.9'''
                            aspect_term = extract_aspect_opinion(item.strip().lower(), "aspect", "opinion")
                            opinion_term = extract_aspect_opinion(item.strip().lower(), "opinion", "sentiment")
                            sentiment = extract_aspect_opinion(item.strip().lower(), "sentiment", "confidence")

                            final['aspect']['content'] = aspect_term.split("-",1)[1].replace(";", "")
                            final['opinion']['content'] = opinion_term.split("-",1)[1].replace(";", "")
                            final['sentiment'] = sentiment.split("-",1)[1].replace(";", "")
                        else:
                            for item2 in item.split(","):
                                key, value = item2.split("-")
                                key = keys_definition(key)
                                if key == 'aspect' or key == 'opinion':
                                    final[key]['content'] = value.strip()
                                else:
                                    final[key] = value.strip()
                        string_index = testing(row["content:string"],textRemoveSymbols(final['aspect']['content']),textRemoveSymbols(final['opinion']['content']))
                        if string_index != []:
                            final['aspect']['token_start'] = string_index[0][0]
                            final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(final['aspect']['content']))
                            final['opinion']['token_start'] = string_index[0][1]
                            final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(final['opinion']['content']))
                        final_dict["triplets"].append(final)
                    elif "," in result:
                        final = {}
                        final['aspect'] = {}
                        final['opinion'] = {}
                        if ": aspect term," in result.strip().lower():
                            '''1. Gameplay: aspect term, solid: opinion term, positive: sentiment, 0.9: confidence score'''
                            #print(row["content:string"])
                            if len(result.split(","))== 4:
                                for item in result.split(","):
                                    if ":" in item:
                                        value, key = item.split(":")
                                        key = keys_definition(key)
                                        if isFloat(value) == False:
                                            value = textRemoveNumbersAndSymbols(value)
                                        if key == 'aspect' or key == 'opinion':
                                            final[key]['content'] = value.strip()
                                        else:
                                            final[key] = value.strip()
                                    elif isFloat(item) == True:
                                        final['confidence'] = item
                            else:
                                '''1. cash shop: aspect term, buggy mess: aspect term, missing content from launch: aspect term, crafting: aspect term, private/solo lobbies: aspect term, weapons from trailer: aspect term, prioritize fixing cash shop bugs: opinion term, negative sentiment, 0.9 confidence score'''
                                aspect_arr = []
                                if result.count('aspect term') > 1:
                                    for item in result.split(","):
                                        if "aspect term" in item.strip().lower():
                                            aspect_arr.append(textRemoveNumbersAndSymbols(item.split(":")[0]))
                                            final['aspect']['content'] = ",".join(aspect_arr)
                                        elif "opinion term" in item.strip().lower():
                                            final['opinion']['content'] = item.split(":")[0]
                                        elif "sentiment" in item.strip().lower():
                                            final['sentiment'] = item.strip().split(" ")[0]
                                        elif "confidence score" in item.strip().lower():
                                            final['confidence'] = item.strip().split(" ")[0]
                            if final['aspect'] != {} and final['opinion'] != {}:
                                string_index = testing(row["content:string"],textRemoveSymbols(final['aspect']['content']),textRemoveSymbols(final['opinion']['content']))
                                if string_index != []:
                                    final['aspect']['token_start'] = string_index[0][0]
                                    final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(final['aspect']['content']))
                                    final['opinion']['token_start'] = string_index[0][1]
                                    final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(final['opinion']['content']))
                                final_dict['triplets'].append(final)
                            else:
                                continue
                        elif ": aspect term-" in result.lower():
                            '''1. Cash-shop: aspect term-cash-shop, opinion term-works flawlessly, sentiment-positive, confidence score-1'''
                            if ":" in result:
                                item = result.split(":")[1]
                                if item.count(",") == 3:
                                    for item2 in item.split(","):
                                        if item2.count("-") > 1:
                                            key = item2.split("-",1)[0]
                                            key = keys_definition(key)
                                            value = item2.split("-",1)[1]
                                            if key == 'aspect' or key == 'opinion':
                                                final[key]['content'] = value.strip()
                                            else:
                                                final[key.strip()] = value.strip()
                                        else:
                                            key, value = item2.split("-")
                                            if keys_definition(key) == 'aspect' or keys_definition(key) == 'opinion':
                                                final[keys_definition(key)]['content'] = value.strip()
                                            else:
                                                final[keys_definition(key)] = value.strip()
                                else:
                                    '''12. Gameplay itself: aspect term- gameplay itself, opinion term- fun, barring the chip damage, sentiment- positive, confidence score- 0.8'''
                                    aspect_term = None
                                    opinion_term = None
                                    sentiment = None
                                    confidence_score = None
                                    substrings = item.split(",")
                                    # Extract the aspect term, opinion term, and sentiment
                                    for substring in substrings:
                                        if substring.strip().startswith("aspect term"):
                                            aspect_term = substring.split("-")[1].strip()
                                            final['aspect']['content'] = aspect_term
                                        elif substring.strip().startswith("opinion term"):
                                            opinion_term = substring.split("-")[1].strip()
                                            final['opinion']['content'] = opinion_term
                                        elif substring.strip().startswith("sentiment"):
                                            sentiment = substring.split("-")[1].strip()
                                            final['sentiment'] = sentiment
                                        elif substring.strip().startswith("confidence score"):
                                            confidence_score = substring.split("-")[1].strip()
                                            final['confidence'] = confidence_score
                                string_index = testing(row["content:string"],textRemoveSymbols(final['aspect']['content']),textRemoveSymbols(final['opinion']['content']))
                                if string_index != []:
                                    final['aspect']['token_start'] = string_index[0][0]
                                    final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(final['aspect']['content']))
                                    final['opinion']['token_start'] = string_index[0][1]
                                    final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(final['opinion']['content']))
                                final_dict["triplets"].append(final)
                        elif ": aspect term -" in result.lower():
                            '''1. optional cosmetics: aspect term - cosmetics, opinion term - optional, sentiment - negative, confidence score - 0.8'''
                            #print(row["content:string"])
                            #for item in result.split(","):
                            if ":" in result:
                                item = result.split(":")[1]
                                if item.count(",") == 3:
                                    for item2 in item.split(","):
                                        if item2.count("-")>1:
                                            dash_index = item2.index("-")
                                            key = item2[:dash_index+1]
                                            value = item2[dash_index + 2:]
                                            if keys_definition(key) == 'aspect' or keys_definition(key) == 'opinion':
                                                final[keys_definition(key)]['content'] = value.strip()
                                            else:
                                                final[keys_definition(key)] = value.strip()
                                        else:
                                            key, value = item2.split("-")
                                            if keys_definition(key) == 'aspect' or keys_definition(key) == 'opinion':
                                                final[keys_definition(key)]['content'] = value.strip()
                                            else:
                                                final[keys_definition(key).strip()] = value.strip()
                                else:
                                    '''3. large, bloated companies: aspect term - companies, opinion term - large, bloated, sentiment - negative, confidence score - 0.9'''
                                    aspect_term = None
                                    opinion_term = None
                                    sentiment = None
                                    confidence_score = None
                                    substrings = item.split(",")
                                    # Extract the aspect term, opinion term, and sentiment
                                    for substring in substrings:
                                        if substring.strip().startswith("aspect term"):
                                            aspect_term = substring.split("-")[1].strip()
                                            final['aspect']['content'] = aspect_term
                                        elif substring.strip().startswith("opinion term"):
                                            opinion_term = substring.split("-")[1].strip()
                                            final['opinion']['content'] = opinion_term
                                        elif substring.strip().startswith("sentiment"):
                                            sentiment = substring.split("-")[1].strip()
                                            final['sentiment'] = sentiment
                                        elif substring.strip().startswith("confidence score"):
                                            confidence_score = substring.split("-")[1].strip()
                                            final['confidence'] = confidence_score
                            else:
                                if "-" not in item:
                                    continue
                                else:
                                    if len(item.split('-')) > 2:  #opinion term - scummy cash-grab
                                        key = item.split('-')[0]
                                        value = "-".join(item[1:])
                                    else:
                                        key,value = item.split("-")
                                if keys_definition(key) == 'aspect' or keys_definition(key) == 'opinion':
                                    final[keys_definition(key)]['content'] = value.strip()
                                else:
                                    final[keys_definition(key).strip().lower()] = value.strip()
                            string_index = testing(row["content:string"],textRemoveSymbols(final['aspect']['content']),textRemoveSymbols(final['opinion']['content']))
                            if string_index != []:
                                final['aspect']['token_start'] = string_index[0][0]
                                final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(final['aspect']['content']))
                                final['opinion']['token_start'] = string_index[0][1]
                                final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(final['opinion']['content']))
                            final_dict['triplets'].append(final)
                        elif "(aspect:" in result.strip().lower():
                            if result.count(",") > 3:
                                continue
                            else:
                                for item in result.split(","):
                                    split_string = item.strip().split(": ")
                                    key = split_string[0]
                                    value = ": ".join(split_string[1:])
                                    # res = "".join(filter(lambda x: not x.isdigit(), key))
                                    # res = re.sub(r'[^\w]', ' ', res)
                                    if keys_definition(key) == 'aspect' or keys_definition(key) == 'opinion':
                                        final[keys_definition(key)]['content'] = value.strip().replace(')', "")
                                    else:
                                        final[keys_definition(key)] = value.strip().replace(')', "")
                            string_index = testing(row["content:string"],textRemoveSymbols(final['aspect']['content']),textRemoveSymbols(final['opinion']['content']))
                            if string_index != []:
                                final['aspect']['token_start'] = string_index[0][0]
                                final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(final['aspect']['content']))
                                final['opinion']['token_start'] = string_index[0][1]
                                final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(final['opinion']['content']))
                            final_dict['triplets'].append(final)
                        elif "(aspect term)" in result.strip().lower():
                            '''2. Setting (aspect term), well-realized, darkly beautiful (opinion term), positive (sentiment), 0.9 (confidence score)'''
                            #print(row["content:string"])
                            if len(result.split(")")) == 1:
                                continue
                            else:
                                for item in result.split(")"):
                                    if item == "" or item == " "or item == "\n" or len(item.split("(")) == 1:
                                        continue
                                    else:
                                        value, key = item.split("(")
                                        key = keys_definition(key)
                                        if "aspect" in key:
                                            value = textRemoveNumbersAndSymbols(value)
                                            if key == 'aspect' or key == 'opinion':
                                                final[key]['content'] = value.strip()
                                            else:
                                                final[key] = value.strip()
                                        else:
                                            value = value.replace(",", "")
                                            if key == 'aspect' or key == 'opinion':
                                                final[key]['content'] = value.strip()
                                            else:
                                                final[key.strip()] = value.strip()
                                string_index = testing(row["content:string"],textRemoveSymbols(final['aspect']['content']),textRemoveSymbols(final['opinion']['content']))
                                if string_index != []:
                                    final['aspect']['token_start'] = string_index[0][0]
                                    final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(final['aspect']['content']))
                                    final['opinion']['token_start'] = string_index[0][1]
                                    final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(final['opinion']['content']))
                                final_dict["triplets"].append(final)
                        elif "- aspect term" in result.strip().lower():
                            for item in result.split(","):
                                key,value = item.split("- ")
                                value = keys_definition(value)
                                if value == 'aspect' or value == 'opinion':
                                    final[value]['content'] = key.strip()
                                else:
                                    final[value] = key.strip()
                            
                            string_index = testing(row["content:string"],textRemoveSymbols(final['aspect']['content']),textRemoveSymbols(final['opinion']['content']))
                            if string_index != []:
                                final['aspect']['token_start'] = string_index[0][0]
                                final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(final['aspect']['content']))
                                final['opinion']['token_start'] = string_index[0][1]
                                final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(final['opinion']['content']))
                            final_dict['triplets'].append(final)
                        elif "aspect term:" in result.strip().lower() and "opinion term:" in result.strip().lower() and "sentiment" in result.strip().lower() and "confidence score" in result.strip().lower():
                            #print(row["content:string"])
                            if check_sentiment_follows_aspect(result.strip().lower(), "opinion term: ") == False:
                                '''1. aspect term: features, sentiment: negative, opinion term: not there, confidence score: 0.8'''
                                sentence = result.strip().lower()
                                aspect_term = extract_aspect_opinion(sentence, "aspect term", "sentiment")
                                opinion_term = extract_aspect_opinion(sentence, "opinion term", "confidence score")
                                sentiment = extract_aspect_opinion(sentence, "sentiment", "opinion term")
                                final['aspect']['content'] = aspect_term.split(":")[1]
                                final['opinion']['content'] = opinion_term.split(":")[1]
                                final['sentiment'] = sentiment.split(":")[1]
                            else:
                                '''1. Aspect Term: God Emporers will, Imperial ethos  Opinion Term: absolute, unadulterated HERESY  Sentiment: Negative  Confidence Score: 1'''
                                sentence = result.strip().lower()
                                aspect_term = extract_aspect_opinion(sentence, "aspect term", "opinion term")
                                opinion_term = extract_aspect_opinion(sentence, "opinion term", "sentiment")
                                sentiment = extract_aspect_opinion(sentence, "sentiment", "confidence score")
                                final['aspect']['content'] = aspect_term.split(":")[1]
                                final['opinion']['content'] = opinion_term.split(":")[1]
                                final['sentiment'] = sentiment.split(":")[1]
                            string_index = testing(row["content:string"],textRemoveSymbols(final['aspect']['content']),textRemoveSymbols(final['opinion']['content']))
                            if string_index != []:
                                final['aspect']['token_start'] = string_index[0][0]
                                final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(final['aspect']['content']))
                                final['opinion']['token_start'] = string_index[0][1]
                                final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(final['opinion']['content']))
                            final_dict['triplets'].append(final)
                        else:
                            if ";" in result:
                                continue
                            else:
                                if ("aspect" not in result.strip().lower()) and ("opinion" not in result.strip().lower())and ("sentiment" not in result.strip().lower()) and (len(result.split(","))<4):
                                    continue
                                elif ("aspect" not in result.strip().lower()) and ("opinion" not in result.strip().lower())and ("sentiment" not in result.strip().lower()):
                                    final['aspect']['content'] = textRemoveNumbersAndSymbols(result.split(",")[0])
                                    final['opinion']['content'] = result.split(",")[1]
                                    final['sentiment'] = result.split(",")[2]
                                    final['confidence'] = result.split(",")[3]
                                else:
                                    #print(row["content:string"])
                                    if "aspect term" not in result.strip() and "opinion term" in result.strip() and "sentiment" in result.strip():
                                        '''3. enjoy the game: opinion term, positive sentiment, 0.9 confidence score'''
                                        final['aspect'] = ''
                                        for item in result.split(","):
                                            if ":" in item:
                                                value, key = item.split(":")
                                                value = value.split(".",1)[1]
                                                if keys_definition(key) == 'aspect' or keys_definition(key) == 'opinion':
                                                     final[keys_definition(key)]['content'] = value.strip()
                                                else:
                                                    final[keys_definition(key)] = value.strip()
                                            else:
                                                if isFloat(item.strip().split(" ")[0]):
                                                    final['confidence'] = item.strip().split(" ")[0]
                                                else:
                                                    if keys_definition(item.strip().split(" ")[1]) == 'aspect' or keys_definition(item.strip().split(" ")[1]) == 'opinion':
                                                        final[keys_definition(item.strip().split(" ")[1]) ] = item.strip().split(" ")[0]
                                                    else:
                                                        final[keys_definition(item.strip().split(" ")[1]) ] = item.strip().split(" ")[0]
                                    elif "aspect term, positive sentiment" in result.strip() or "aspect term, negative sentiment" in result.strip() \
                                        or "opinion term, positive sentiment" in result.strip() or "opinion term, negative sentiment" in result.strip():
                                        #print(row["content:string"])
                                        continue
                                    else:
                                        for item in result.split(","):
                                            if item == ' ' or '':
                                                continue
                                            elif len(item.strip().split(":")) >2: #need to fix
                                                #print(row['content:string'])
                                                continue
                                            elif "(" in result: 
                                                continue
                                            else:
                                                if len(item.strip().split(":")) <2:
                                                    key = result.split(":")[0]
                                                    value = result.split(":")[1]
                                                    #final[key.strip().lower()] = value.strip()
                                                else:
                                                    key, value = item.strip().split(":")
                                                    if "\"" in value:
                                                        value = value.replace("\"", "")
                                                if keys_definition(key) == 'aspect' or keys_definition(key) == 'opinion':
                                                    final[keys_definition(key)]['content'] = value.strip()
                                                else:
                                                    final[keys_definition(key)] = value.strip()
                                if final['aspect'] != {} and final['opinion']!= {} and final['aspect'] != '':
                                    string_index = testing(row["content:string"],textRemoveSymbols(final['aspect']['content']),textRemoveSymbols(final['opinion']['content']))
                                    if string_index != []:
                                        final['aspect']['token_start'] = string_index[0][0]
                                        final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(final['aspect']['content']))
                                        final['opinion']['token_start'] = string_index[0][1]
                                        final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(final['opinion']['content']))
                                final_dict['triplets'].append(final)
                    elif "(aspect term) - " in result:
                        '''1. portrayal of the 40k universe (aspect term) - great (opinion term) - positive (sentiment) - 0.9 (confidence score)'''
                        #print(row["content:string"])
                        final = {}
                        final['aspect'] = {}
                        final['opinion'] = {}
                        if result.count("-") > 3:
                            for item in result.split(")"):
                                if item == "" or item == " ":
                                    continue
                                else:
                                    key,value = item.split("(")
                                    if keys_definition(key) == 'aspect' or keys_definition(key) == 'opinion':
                                        final[keys_definition(key)]['content'] = value.strip()
                                    else:
                                        final[keys_definition(key)] = value.strip()
                        else:
                            for item in result.split("-"):
                                value, key = item.split("(")
                                if "aspect term" in key:
                                    value = textRemoveNumbersAndSymbols(value)
                                else:
                                    key = key.replace(")", "")
                                if keys_definition(key) == 'aspect' or keys_definition(key) == 'opinion':
                                    final[keys_definition(key)]['content'] = value.strip()
                                else:
                                    final[keys_definition(key)] = value.strip()
                        if final['aspect'] != {} and final['opinion']!= {}:
                            string_index = testing(row["content:string"],textRemoveSymbols(final['aspect']['content']),textRemoveSymbols(final['opinion']['content']))
                            if string_index != []:
                                final['aspect']['token_start'] = string_index[0][0]
                                final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(final['aspect']['content']))
                                final['opinion']['token_start'] = string_index[0][1]
                                final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(final['opinion']['content']))
                        final_dict["triplets"].append(final)
                    elif "Aspect Term: " in result or "aspect term: " in result:
                        if result.count(":")>1:
                            final = {}
                            final['aspect'] = {}
                            final['opinion'] = {}
                            if "Sentiment: \"<NULL>\"" in result:
                                '''1. Aspect Term: "Two handed chainsword"  Opinion Term: "<NULL>"  Sentiment: "<NULL>"  Confidence Score: 0'''
                                continue
                            elif "\"" not in result:
                                '''2. Aspect Term: cooperative shooter  Opinion Term: taking the p*%s  Sentiment: Negative  Confidence Score: 1'''
                                sentence = result.strip().lower()
                                aspect_term = extract_aspect_opinion(sentence, "aspect term", "opinion term")
                                opinion_term = extract_aspect_opinion(sentence, "opinion term", "sentiment")
                                sentiment = extract_aspect_opinion(sentence, "sentiment", "confidence score")

                                final['aspect']['content'] = aspect_term.split(":")[1]
                                final['opinion']['content'] = opinion_term.split(":")[1]
                                final['sentiment'] = sentiment.split(":")[1]
                            elif result.count("\"") > 3:
                                '''1. Aspect Term: "Gameplay"  Opinion Term: "Crashed"  Sentiment: "Negative"  Confidence Score: 0.9'''
                                sentence = result.strip().lower()
                                aspect_term = extract_aspect_opinion(sentence, "aspect term", "opinion term")
                                opinion_term = extract_aspect_opinion(sentence, "opinion term", "sentiment")
                                sentiment = extract_aspect_opinion(sentence, "sentiment", "confidence score")
                                final['aspect']['content'] = textRemoveNumbersAndSymbols(aspect_term.split(":")[1])
                                final['opinion']['content'] = textRemoveNumbersAndSymbols(opinion_term.split(":")[1])
                                final['sentiment'] = textRemoveNumbersAndSymbols(sentiment.split(":")[1])

                            else:
                                '''1. Aspect Term: "Warhammer 40k universe"  Opinion Term: "insignificant"  Sentiment: Negative  Confidence Score: 0.9'''
                                final['aspect']['content'] = result.split("\"")[1]
                                final['opinion']['content'] = result.split("\"")[3]
                                item = result.split("\"")[4]
                                final['sentiment'] = item.split(":")[1].replace("Confidence Score" , "")
                                final['confidence'] = item.split(":")[2]
                        else: 
                            '''2. Aspect Term: Game Play '''
                            final = {}
                            final['aspect'] = {}
                            final['opinion'] = {}
                            key,value = result.split(":")
                            if keys_definition(key) == 'aspect' or keys_definition(key) == 'opinion':
                                final[keys_definition(key)]['content'] = value.strip()
                            else:
                                final[keys_definition(key)] = value.strip()
                        if final['aspect'] != {} and final['opinion']!= {}:
                            string_index = testing(row["content:string"],textRemoveSymbols(final['aspect']['content']),textRemoveSymbols(final['opinion']['content']))
                            if string_index != []:
                                final['aspect']['token_start'] = string_index[0][0]
                                final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(final['aspect']['content']))
                                final['opinion']['token_start'] = string_index[0][1]
                                final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(final['opinion']['content']))
                        final_dict["triplets"].append(final)
                elif "aspect:" in result and "opinion:" in result and "sentiment:" in result:
                    #print(row["content:string"])
                    final = {}
                    final['aspect'] = {}
                    final['opinion'] = {}
                    if "," in result:
                        '''Runs awful, aspect: performance, opinion: awful, sentiment: negative, confidence: 1'''
                        for item in result.split(","):
                            if ":" not in item:
                                continue
                            else:
                                key, value = item.split(":")
                                if keys_definition(key) == 'aspect' or keys_definition(key) == 'opinion':
                                    final[keys_definition(key)]['content'] = value.strip()
                                else:
                                    final[keys_definition(key)] = value.strip()
                        string_index = testing(row["content:string"],textRemoveSymbols(final['aspect']['content']),textRemoveSymbols(final['opinion']['content']))
                        if string_index != []:
                            final['aspect']['token_start'] = string_index[0][0]
                            final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(final['aspect']['content']))
                            final['opinion']['token_start'] = string_index[0][1]
                            final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(final['opinion']['content']))
                    elif "-" in result:
                        '''Game - aspect: current state - opinion: can't - sentiment: negative - confidence: 1'''
                        item = result.split("-", 1)[1]
                        for item2 in item.split("-"):
                            key, value = item2.split(":")
                            if keys_definition(key) == 'aspect' or keys_definition(key) == 'opinion':
                                final[keys_definition(key)]['content'] = value.strip()
                            else:
                                final[keys_definition(key)] = value.strip()
                    final_dict['triplets'].append(final)
                elif ("opinion term" in result.strip().lower() or "sentiment" in result.strip().lower() or "confidence score" in result.strip().lower()) and "aspect term" not in result.strip().lower():
                    '''
                    1. Aspect Term: Co-op game, class and weapon options, Darktide, modern PC, CPU, and/or GPU, 
                        Opinion Term: excellent, highly recommend, plenty of fun, 
                    '''
                    #print(row["content:string"])
                    if "(positive sentiment)" in result or ("sentiment" in result and "confidence" in result):
                        continue
                    elif "|" in result and ":" in result:
                        '''Game | Aspect: Performance | Opinion: Poor | Sentiment: Negative | Confidence: 0.8'''
                        final = {}
                        final['aspect'] = {}
                        final['opinion'] = {}
                        final['aspect']['content'] = (result.split("|")[1]).split(":")[1]
                        final['opinion']['content'] = (result.split("|")[2]).split(":")[1]
                        final['sentiment'] = (result.split("|")[3]).split(":")[1]
                        final['confidence'] = (result.split("|")[4]).split(":")[1]
                        string_index = testing(row["content:string"],textRemoveSymbols(final['aspect']['content']),textRemoveSymbols(final['opinion']['content']))
                        if string_index != []:
                            final['aspect']['token_start'] = string_index[0][0]
                            final['aspect']['token_end'] = int(string_index[0][0]) + len(nlp(final['aspect']['content']))
                            final['opinion']['token_start'] = string_index[0][1]
                            final['opinion']['token_end'] = int(string_index[0][1]) + len(nlp(final['opinion']['content']))
                    elif ":" in result:
                        key, value = result.split(":")
                        if keys_definition(key) == 'aspect' or keys_definition(key) == 'opinion':
                            final[keys_definition(key)]['content'] = value.strip()
                        else:
                            final[keys_definition(key)] = value.strip()

        final2_arr.append(final_dict)

    with open("data.json", "w") as f: #A Json file that stored the sentences of emoji between text
        json.dump(final2_arr, f, ensure_ascii=False, indent=4)