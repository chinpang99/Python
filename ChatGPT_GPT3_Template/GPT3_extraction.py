#link : https://www.youtube.com/watch?v=TdNSj_qgdFk&ab_channel=BhaveshBhatt
from pychatgpt import ChatGPT
import pandas as pd
import time
import openai
import xlsxwriter
import os
import argparse


def chatGPT(message:str, api):
    initial_sentence = "Extract a list  from the sentence, each item of the list contains aspect term, opinion term and sentiment as well as confidence score from 0 to 1. \n"
    message = " ".join([initial_sentence,message])
    time.sleep(10)
    response = api.send_message(message)
    return response["message"]

max_retry = 0
def gpt3(sentence:str):
  global max_retry
  try:
    print("Processing: " + sentence)
    statement = 'Extract a list  from the sentence, each item of the list contains aspect term, opinion term and sentiment as well as confidence score from 0 to 1.'
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt= statement + "\n \"" + sentence + " \"",
        temperature=0.1,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
      )
    result = response['choices'][0]['text']
    max_retry=0
  except:
    result = "#ERROR"
    if max_retry >5:
      pass
    else:
      print("Error, sleep 1.5 minutes")
      time.sleep(95)
      max_retry+=1
  return result



if __name__ == "__main__":
    start = time.time()
    parser = argparse.ArgumentParser()
    user_environment = os.environ["USER"]
    parser.add_argument(
        "--input_path",
        default="/Users/{user_environment}/Desktop/".format(user_environment = user_environment),
        required=False,
        type=str,
        help="Insert input path"
    )
    parser.add_argument(
        "--output_path",
        default="/Users/{user_environment}/Desktop/".format(user_environment = user_environment),
        required=False,
        type=str,
        help="Insert result output path"
    )
    parser.add_argument(
      "--selection",
      default="gpt3",
      type=str,
      help="Choose either gpt3 or chatgpt"
    )
    args = parser.parse_args()

    if args.selection == "gpt3":
      # GPT3 Script
      # Get OpenAI API Key from this link >> https://beta.openai.com/account/api-keys
      openai.api_key = 'REFER_THE_LINK_TO_GET_API_KEYS'
      df1 = pd.read_csv(args.input_path)
      df1['result'] = df1['content:string'].apply(lambda x: gpt3(x))
    else:
      #ChatGPT Script
      # Get session token from Inspect => Application => Cookies
      session_token = ''    
      api = ChatGPT(session_token)
      df1 = pd.read_csv(args.input_path)
      df1["result"] = df1["content:string"].apply(lambda x: chatGPT(x, api))
      df1


    os.chdir(args.output_path)
    file_name = 'GPT3_result.xlsx'
    workbook = xlsxwriter.Workbook(file_name)
    with pd.ExcelWriter(file_name) as writer:
        df1.to_excel(writer, sheet_name='result', index= False)
    
    

