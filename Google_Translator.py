import requests
import json
import html

def google_translate(content):
        """
        content:待翻译原文
        target_language:翻译目标语言
        """
        source_language=""
        target_language = 'en'
        tranl_content_list = []
        content = content.replace("#"," ").replace("&"," ")
        if not source_language:
            url = "https://translation.googleapis.com/language/translate/v2?target={}&key=AIzaSyB-K2x5lb_VFYQ_w7Ln8EPNIsRxknuZHhU&q={}".format(
                target_language, content)
        else:
            url = "https://translation.googleapis.com/language/translate/v2?source={}&target={}&key=AIzaSyB-K2x5lb_VFYQ_w7Ln8EPNIsRxknuZHhU&q={}".format(
                source_language, target_language, content)
        tranl_content = ""
        try:
            r = requests.get(
                url=url,
            )
            result = json.loads(r.text)
            tranl_content = result["data"]["translations"][0]["translatedText"]
            tranl_content = html.unescape(tranl_content)
        except Exception as e:
            print(str(e))
        tranl_content_list.append(tranl_content)
        return tranl_content

if __name__ == "__main__":
    import pandas as pd
    df1 = pd.read_csv(r'text.csv')
    df1['result_en'] = df1['content'].apply(google_translate)
    df1.to_excel("output.xlsx",sheet_name='Sheet_name_1')  