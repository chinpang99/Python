# emot:3.1 library

Emot is a python library to extract the emojis and emoticons from a text(string). All the emojis and emoticons are taken from a reliable source details are listed in source section.

# 4 main functions from emot library
1. emot.emoji:

Input: It has one input: string
Output: It will return dictionary with 4 different value: dict
value = list of emojis
location = list of location list of emojis
mean = list of meaning
flag = True/False. False means library didn't find anything and True means we find something.

2. emot.emoticons

Input: It has one input: string
Output: It will return dictionary with 4 different value: dict
value = list of emoticons
location = list of location list of emoticons
mean = list of meaning
flag = True/False. False means library didn't find anything and True means we find something.

3. emot.bulk_emoji

Input: Two input: List of string and CPU cores pool: list[], int
By default CPU cores pool value is half of total available cores: multiprocessing.cpu_count()/2
Output: It will return list of dictionary with 4 different value: list of dict
value = list of emojis
location = list of location list of emojis
mean = list of meaning
flag = True/False. False means library didn't find anything and True means we find something.

4. emot.bulk_emoticons

Input: Two input: List of string and CPU cores pool: list[], int
By default CPU cores pool value is half of total available cores: multiprocessing.cpu_count()/2
Output: It will return list of dictionary with 4 different value: list of dict
value = list of emoticons
location = list of location list of emoticons
mean = list of meaning
flag = True/False. False means library didn't find anything and True means we find something.


source from: https://github.com/NeelShah18/emot