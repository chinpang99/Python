#link : https://www.youtube.com/watch?v=TdNSj_qgdFk&ab_channel=BhaveshBhatt
from pychatgpt import ChatGPT
import pandas as pd
import time
import openai
import xlsxwriter
import os
import argparse

def chatGPT(message:str, api):
    initial_sentence = "Extract each aspect term, opinion term and sentiment from the sentence: \n"
    message = " ".join([initial_sentence,message])
    response = api.send_message(message)
    return response["message"]

def gpt3(sentence:str):
  try:
    print("Processing: " + sentence)
    statement = 'Extract a list  from the sentence, each item of the list contains aspect term, opinion term and sentiment as well as confidence score from 0 to 1:'
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt= statement + "\n " + sentence + "",
        temperature=0.1,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
      )
    result = response['choices'][0]['text']
  except:
    result = "#ERROR"
    print("Error, sleep 1.5 minutes")
    time.sleep(95)
    return result


if __name__ == "__main__":
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
    args = parser.parse_args()

    #ChatGPT Script
    # session_token = '' #can refer the YouTube video to get the session_token
    # api = ChatGPT(session_token)
    # df1 = pd.read_csv(r'/Users/chinpangchia/Desktop/testing.csv')
    # df1["result"] = df1["content"].apply(lambda x: chatGPT(x, api))
    # df1


    # GPT3 Script
    # Get OpenAI API Key from this link >> https://beta.openai.com/account/api-keys
    openai.api_key = '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'

    for filename in os.listdir(args.input_path):
      if not filename.endswith(".xlsx"):
        continue
      f = os.path.join(args.input_path, filename)
      print(f'Processing {f}')
      df1 = pd.read_excel(f)
      df1['result'] = df1['content'].apply(lambda x: gpt3(x)).str.replace(r'\n', '')

      os.chdir(args.output_path)
      file_name = 'GPT3_result.xlsx'
      workbook = xlsxwriter.Workbook(file_name)
      with pd.ExcelWriter(file_name) as writer:
          df1.to_excel(writer, sheet_name='result', index= False)

