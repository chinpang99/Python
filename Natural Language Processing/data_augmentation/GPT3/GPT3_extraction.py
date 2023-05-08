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
    args = parser.parse_args()

    #ChatGPT Script
    #session_token = 'eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..OZi8lFF8Rf25SyLo.OXWZOEEYhyAISi0lDmmhX106EaMvrjHtTuE_d6jLjoOtbrLU5jYEotv1zFyiQoKGlj2hTOhP1sNKgmVJ_h9psNIc_c0kS0Q1kewELLrExShlh_qiLblsGFDtADlcSvXgaLH2jZpXPMbmzn608ezndCSWCCY6q3eoX1CSXkl-JLQhEmKRvJxCgo6WbriM1AAzok66QGhGmUQCb4ijpm7kpd58tvuGgHeO-Q_dzfRpk50aFgaJ421s8JgLnIZUE-Tor6W9corvR2BZJTujMHmTfalvNRnOP331gw0zy9-lilUWd0cp1RiWdkwBb8uhsAi__SO104CaVYVYRenWivd438nWW9v65v4qEPmQn5kB6lDAXXE241BbcOLrP_FXgXMon9AavwU3HmF4vUmUZCu7EulWvpAIWDljexmfrBwaT2I_-BnmgrxvbK1xyTdApPOow_ju4Isq80ekab1dqRLqYPkVLwbAQIZ7L7lyM1kDyB1D23Hfp2H9aX5pwkEiAQ6QgQjc-NS5_xMHu5tyqaJ9NFfirqEBkn0AzEainshIPHyoAGFS36NdEmnFX9SydB0czU3n9nQSVB3UdSJQeBKzCnFsi0bjfQRMKHMHlup6_jm4-2VAwt1qAivmYwNJ8YRyBynaYMyq2gtqdKgATeRE0xsEHCAPgt3o1MKWbydM00uwZ9NjPquJ5yEIlp62fF5wFITmk6IOX-m4fFRvZR7dv1Bkuc6J-6GXXm31ZbbwO2ABJ7evUrWuM22NokFgnhRNuFTCEKbSQzQbAJCHFWeLf1lkCWrDoKMyIR3WU9FXhG4Y4fMuRNRmhqCre14kNgI3n1yCWhArAcGBlozFY3zCRcGd6vbZ0ymdA4-DYxe4YrGfWczEjdmU3ouQc6tzk7tTlc1_4QCg8d7WnHEPTUSDt-DpAd7fWuW4_VHOrydQ6OnVV-Vq2BMnRW0Cwx4B7mX0pfgA6A0rRb0hnJAL9ujxQyAkX_AfnBoUaWXHg199GCS94aGcC8ll-f4IItXAd14aX-pYpcP4nVxb1sZK22oyk94DMSKfZOe7tW5pQcxRCucZmBg9__v3yzzZ2PPbK8ptLwV9VtAXN-VsM31CPPT8Kqc9Y2R46JPazeg7x_WMaToYF2BRccYYw5vrIczJKrxJqJtrSkquXCuJhTTDLTIUnAaFdXwdPPpEPjf2SQ0_ruIaAXQz46WpvLskAa6hOf2m-Jmu6sHC1oky2DooeloojPV4cGPjOMvHer5a2p_e2oE71TlgAhFO8d6e0fDYdhoFeIc-kX3nxjuAo0raR_SX50xIr8SJiflh4DRGVyqxvNt4CHEc2hGlveGSvugV05SVszUHvsWzZW9j2WWmZ8p4Z2RqMcGdr2d6Jv3XBa3THPQ25g7fHUxep_7cWszdJMlODJNr5nhMvOwasy2HYnp_7-1KiRxkFg3uea1tnoBWWIswMBWgyhTHRfW7QuroGGnnEJGZrvbrYguWBGHSt16NFYHo2a5U8WaOBiAi0lB8FgJapdPT9qK1gVvk2LOpj7Z6X5Pagv4067HJTGlqo9X6trOyESIfgotv2mpOfF8sZt-yX6AwIxjzNiE27wq9h2SzjdRZUMS9iIMlXL-ifFyKa73b_3YZP28S9G6Jno2dqBzQGSK1YQISN-L5PeDIvDmgjmEi6mAsTZhJK_p9DNqM8q3zCgeFb-lxym2uQNNEkUxpmKpgI_7afQ61rCAOkjVrG5nX5gUFGtNjyyC41JS4q4lgZTkU0HLzlF5P_Iy2QObpt3AWg0CU5eoeEtGpJHoOvlMfVEHCQLGmX4OQhj08cPz9JbT63H_JodsPY5x0u71x8WaheD3mdOJOtsViecKlN05mETZoHUeubp4Q6sTgOwWSN-8e1H0c7TD0AOdVdttTWZ2ufo7Bziml_5Wr7_t6PhYvtB2XCsBFzcdKhXhMSJX-K5sRwV4YkLcre8y5mWGjW322cNJJGyeePLLah66VsCZ6pAnnFRiy90793cL_UDyD9DQyoUTmmDxMF_eSrCHqbGNuPQ4tte3YItgMJhqCdURH1PI2oi4srIUKnzMkGgAx32lMePd0PWXfin4LU7JCaaKuT1rzLZHozWkaBBLzd3cr0XTJ2Uz5VkDEB2e7ofQDY-v4pKrRLUWvudCM_hASPp9_k9AFHPo9gs5N0J0k4edzyKUgXMXaftMt8zk7Ghpm5QDmUEok9yuxPNDMrA6o-4JZ1xCLTu0PqqDjuMZraf_iGZ4UFwjDWHiUpEQOW4KeeBqUZ-8bvAPtEtiYmG9f5608C__SOfYhmbkIuHqFalplO2AL0sRhv_3ODnv4UtRpCrU8JAbyWj4PWuZIsD4ieKGT-r5BaDcjOakdSatncAc7cy_CHaddLcl8Ou2BLRSIf0_K7PFwAhgI_XyLgGLcPXefrd6WfAhi0U5CKBLGuX3Fq2UXTNTDhhFGcJZjqQcFofvTNHv6FgHTD2SRfOebCKVzv-bz6_HxyzSsEUM0aw.ojcrItYyVFriAqDBzSsLcg'    
    session_token = 'eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..ov1Kqm6AH77rKtie.ibBvieZuuYAE5d6mJ2glv_st_2nZTDlLNfQD-xjl7FKG2US7v8mra48oWR3_vuNLU77VPt7T5ZWgW-gWHphZshL3NXcuTVhBw1KzW3DOjnCzyT-xCJlHoMtedzhzoeqcwECdVOKyZmPZgJTWS3rFlmkY3gEdqkr89fjvAFuVdE4vJI6BiSN0cR80TEmcd2GP7RejNq7Y3eEsnt8bZPGz0W1FfRvKlEG2cRglZQBzJdeoJqGq5v45liu7ShGqPUk5l6N-cNigxCapo3RyMZjcPEY8MQ-nRmJEQWurYffwwcva2DCrEkQZZSJrNEkjHu7kKGWRbCQrj1Hrg-Ruh8TRGhLO3LOUTsnh3GaZaAulCD8TkQyeuGXVjKHQmm0alYKHtBMonEhL6HHpTfSA3GT4mRZyqnVrynuKsbgXjxv6M-i-M1WtVGFAz6I9QHZRSEcpF3xkbRbptvK-ZWgH1Hwn_jkwmwkabRrM_dmlxOqFOJ7xxCoENkbRz7zrfCpZu5rbblPgzM5fVqvU9e4so2YDq0EVKZmAXrfcifMQpaOIfqQ6PS2bn5RSxer01UyFm1qEH1vbFJ2qlh8fVaQbZxhPkICSDve9IHqaduLxpkxlANJPj_rkOkv-48YVskSviNjYahxGfW3J-QPlUmJiVoH816f4HgwGaanc7CMcX_tz0FaNL6w1mdxZWAGg1fY1TOEypLc6nlL22imYw8J17_6NWpFySc0qp2-cFTEwNw2wQpKxwBM9bV4Gp-4FmGOLUXX6bZ0YqPiZSjB_6LcHCFJZfuuN-DCS9MizrMcg9fyUbANhX-8DYBcVq5UUhkWoaaKGjho3vw_m_Ks9kf_-rM29eyXp8di-PNg6K74RlS3Zw69ZeR0D4w4l02qegWEl2t8MhC3ADkq_teNmfiU2OIRpi85GACA40YYMnmeCpOV4z5QvkKEg5cB_35XFURnfOVVkWZ7Iii254_toNDW4NT576espj7OKtybxA1uKOOR-UgW7UP-AjXwrcG__lHhf9cPLhVZFk8SsqrD-31X_D5tqv6VEEHi1ac1rpX8B_68jjASrJ927wYr91s8yJ2agwdL8VC__xSfpI2-bIVYY1w0juAcS408u6YfOlIKaGSCirMKHHo-A4Tua7SZbDYA4ne-sZX5Zp4y_Mbby01kEaWrTn3MfDnXO9exQTV07R6p3kmC5vLQfMxktMojBflAcBehGkP7gpHbWgskgMs4Q5iBepKwKETjd6zQZlsGHugdjCxSi6aAWw2tvPrJ3ZB8jpsg1-di1pveF8ebY9u3D1IF9cuANdHhTDzPJIwmmoOtf5Xp2W0fTBLTySE86LDab6ouP4vchxexAfla90_YKEhPZmHRIDX7RbwbF5igrP5mbT4vbRp3Avl2SrTrjchynEb8DE8Bllvp6jtqaE6JtNgHnjs4Tw8cpqih0Ml5_q5Eun8sB28z_8r3_AnThrEdycn1vCSfCsTOZOTLiGpf1cQROWvF78WgMRqsCd3WMiLkxq1vFqVY4o0q9aHdmaF6yvSE9gBMTZbZV0GR7deRy7LkkhJEnJG6sfZ9p6GMnPabIYsrl2mslZ03TTGBr1c363I0if1Y2moDmUQJKNlICduSkQYHoFNbbHCH9iZacwEOyL2VOopIWS9AyaJ_XMncw-5IqWV_wyGJZOi_jyZe19gw5C3Ca4WOLrVtvTJGCBhtzPMH0RGQXXIp22a90LcyjApiMfkMSH4wjW6KBxZ-IctfG9FiwH90yUQ8hbDfaEqvhysZ4fNUdmSXlXj1c209xoGZjWtwQTMuq88p3X1n9R6LzIKSebktB-EJ29CHhWyEGrjoEVFYmBj2gZeg0_EwVH0hyGCMEv79Wf9yrbHdeaKC1WWBdowRcuRoCezSKD86GoZUoxRWLYc_oPL44LTbTGVV-XWXrFWx1gYY7zfIgilxam5EZaqS9VQWP38JQWln4j2t9dc5jXSuQ4e7BFGxRAoMeiyPSzab-ORsvn_QY6j12zoUuzV5qcBn-rRtscCovt_9LP74kCSvnRupo5UT8mccmG8Xe5DL1oYm74RrUzCMpJU2NIr6vk0Hh__ppfYV3s4cz-7c7BHqGR1du7BBy6cHs_HZ5AtQwb20YT_jNluL8Q85Ekz5EADQrKq-5JEnuH0rjBkpKyx8bYKdDYAeD_0OwxKnKPc7C0jf3PotNv7FHj37tTfqIyWnxcr_7e5Nky64aHI7SxmUyGzOIy4LusQsUTVTJ_GretsqNQSFVMPOw0Nvjzz2-LzGl9TVdejHSizczAcMMewq_x-kEJuJZgkyeSxuYiI4-WRhCRB_xYBRlcfMWXE2xgCclc4X8wv6W8E7KhKp91oYtpYqwDFO_zMZK3DZtBMsRbpBV9Zzy6HoWNfB3Df6V5Yuonp8CHl0I-3WMym5kJ_Zt9_e7ptaSdYZ0ZDmBE-Nkoc81fLjZMrzmZgxWf5wAISE0tchyriN_yhDsPqRTBscXRlE.LH6MrqbLy_70582NOsotAA'
    api = ChatGPT(session_token)
    df1 = pd.read_csv(r'/Users/chinpangchia/Desktop/game202212.csv')
    df1 = df1.iloc[:100]
    df1["result"] = df1["content:string"].apply(lambda x: chatGPT(x, api))
    df1


    # GPT3 Script
    # Get OpenAI API Key from this link >> https://beta.openai.com/account/api-keys
    # openai.api_key = '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'
    # #df1 = pd.read_excel(f)
    # df1 = pd.read_csv(r'/Users/chinpangchia/Desktop/game202212.csv')
    # df1 = df1.iloc[5000:5500]
    # df1['result'] = df1['content:string'].apply(lambda x: gpt3(x))

    os.chdir(args.output_path)
    file_name = 'GPT3_result.xlsx'
    workbook = xlsxwriter.Workbook(file_name)
    with pd.ExcelWriter(file_name) as writer:
        df1.to_excel(writer, sheet_name='result', index= False)
    
    end = time.time()
    print(end - start)

