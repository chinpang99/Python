from functools import lru_cache

import openai
import timeout_decorator
import time
from tqdm import tqdm


class ModelAnnotator:
    def __init__(self, prompt_prefix, prompt_suffix, annotator_name=None, pause_time=None):
        self.prompt_prefix = prompt_prefix
        self.prompt_suffix = prompt_suffix
        self.annotator_name = annotator_name
        self.pause_time = pause_time
        self.max_tokens = 1000

    def set_api_key(self, api_key=None):
        if api_key is not None:
            openai.api_key = api_key

    def set_name(self, annotator_name):
        self.annotator_name = annotator_name

    def set_session_token(self, session_token):
        pass

    def set_pause_time(self, pause_time):
        self.pause_time = pause_time

    def set_max_tokens(self, max_tokens):
        self.max_tokens = max_tokens

    def call_model(self, content: str) -> str:
        NotImplemented

    @lru_cache(maxsize=10240)
    def annotate(self, content: str) -> str:
        content = self.prompt_prefix + content + self.prompt_suffix
        annotation = self.call_model(content)
        if self.pause_time is not None:
            time.sleep(self.pause_time)
        return annotation

    def annotate_batch(self, batches):
        results = []
        for content in batches:
            try:
                generated_text = self.annotate(content)
            except Exception as e:
                print(f"Error:{e}")
                generated_text = None
            results.append(generated_text)

        #loop one more round for make up
        for i, content in enumerate(batches):
            if results[i] is None:
                print(f"Rework on batch {i}...")
                try:
                    generated_text = self.annotate(content)
                except Exception as e:
                    print(f"Error:{e}")
                    generated_text = None
                results[i] = generated_text

        return results

    @staticmethod
    def create_annotator(prompt_prefix, prompt_suffix, annotator_name: str):
        if annotator_name == "GPT3":
            AnnotatorClass = GPT3Annotator
        elif annotator_name == "ChatGPT":
            AnnotatorClass = ChatGPTAnnotator
        elif annotator_name == "ChatGPTWeb":
            AnnotatorClass = ChatGPTWebAnnotator
        else:
            raise Exception(f"Unsupported Annotator:{annotator_name}")

        annotator = AnnotatorClass(prompt_prefix, prompt_suffix, annotator_name)
        return annotator


class GPT3Annotator(ModelAnnotator):
    def call_model(self, content, retry=3):
        if retry == 0:
            return None
        try:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=content,
                temperature=0,
                max_tokens=self.max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            return response['choices'][0]['text']
        except openai.error.APIError as e:
            # Handle API error here, e.g. retry or log
            print(f"OpenAI API returned an API Error: {e}")
            pass

        except openai.error.APIConnectionError as e:
            # Handle connection error here
            print(f"Failed to connect to OpenAI API: {e}")
            pass

        except openai.error.RateLimitError as e:
            # Handle rate limit error (we recommend using exponential backoff)
            print(f"Retry due to that OpenAI API request exceeded rate limit: {e}")
            time.sleep(10)
            return self.call_model(content, retry - 1)

        return None


class ChatGPTAnnotator(ModelAnnotator):
    def call_model(self, content, retry=3):
        if retry == 0:
            return None
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": content},
                ]
            )
            return response["choices"][0]["message"]["content"]
        except openai.error.APIError as e:
            # Handle API error here, e.g. retry or log
            print(f"OpenAI API returned an API Error: {e}")
            pass

        except openai.error.APIConnectionError as e:
            # Handle connection error here
            print(f"Failed to connect to OpenAI API: {e}")
            pass

        except openai.error.RateLimitError as e:
            # Handle rate limit error (we recommend using exponential backoff)
            print(f"Retry due to that OpenAI API request exceeded rate limit: {e}")
            time.sleep(10)
            return self.call_model(content, retry - 1)

        return None


class ChatGPTWebAnnotator(ModelAnnotator):
    SESSION_TOKEN = '''eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..OZi8lFF8Rf25SyLo.OXWZOEEYhyAISi0lDmmhX106EaMvrjHtTuE_d6jLjoOtbrLU5jYEotv1zFyiQoKGlj2hTOhP1sNKgmVJ_h9psNIc_c0kS0Q1kewELLrExShlh_qiLblsGFDtADlcSvXgaLH2jZpXPMbmzn608ezndCSWCCY6q3eoX1CSXkl-JLQhEmKRvJxCgo6WbriM1AAzok66QGhGmUQCb4ijpm7kpd58tvuGgHeO-Q_dzfRpk50aFgaJ421s8JgLnIZUE-Tor6W9corvR2BZJTujMHmTfalvNRnOP331gw0zy9-lilUWd0cp1RiWdkwBb8uhsAi__SO104CaVYVYRenWivd438nWW9v65v4qEPmQn5kB6lDAXXE241BbcOLrP_FXgXMon9AavwU3HmF4vUmUZCu7EulWvpAIWDljexmfrBwaT2I_-BnmgrxvbK1xyTdApPOow_ju4Isq80ekab1dqRLqYPkVLwbAQIZ7L7lyM1kDyB1D23Hfp2H9aX5pwkEiAQ6QgQjc-NS5_xMHu5tyqaJ9NFfirqEBkn0AzEainshIPHyoAGFS36NdEmnFX9SydB0czU3n9nQSVB3UdSJQeBKzCnFsi0bjfQRMKHMHlup6_jm4-2VAwt1qAivmYwNJ8YRyBynaYMyq2gtqdKgATeRE0xsEHCAPgt3o1MKWbydM00uwZ9NjPquJ5yEIlp62fF5wFITmk6IOX-m4fFRvZR7dv1Bkuc6J-6GXXm31ZbbwO2ABJ7evUrWuM22NokFgnhRNuFTCEKbSQzQbAJCHFWeLf1lkCWrDoKMyIR3WU9FXhG4Y4fMuRNRmhqCre14kNgI3n1yCWhArAcGBlozFY3zCRcGd6vbZ0ymdA4-DYxe4YrGfWczEjdmU3ouQc6tzk7tTlc1_4QCg8d7WnHEPTUSDt-DpAd7fWuW4_VHOrydQ6OnVV-Vq2BMnRW0Cwx4B7mX0pfgA6A0rRb0hnJAL9ujxQyAkX_AfnBoUaWXHg199GCS94aGcC8ll-f4IItXAd14aX-pYpcP4nVxb1sZK22oyk94DMSKfZOe7tW5pQcxRCucZmBg9__v3yzzZ2PPbK8ptLwV9VtAXN-VsM31CPPT8Kqc9Y2R46JPazeg7x_WMaToYF2BRccYYw5vrIczJKrxJqJtrSkquXCuJhTTDLTIUnAaFdXwdPPpEPjf2SQ0_ruIaAXQz46WpvLskAa6hOf2m-Jmu6sHC1oky2DooeloojPV4cGPjOMvHer5a2p_e2oE71TlgAhFO8d6e0fDYdhoFeIc-kX3nxjuAo0raR_SX50xIr8SJiflh4DRGVyqxvNt4CHEc2hGlveGSvugV05SVszUHvsWzZW9j2WWmZ8p4Z2RqMcGdr2d6Jv3XBa3THPQ25g7fHUxep_7cWszdJMlODJNr5nhMvOwasy2HYnp_7-1KiRxkFg3uea1tnoBWWIswMBWgyhTHRfW7QuroGGnnEJGZrvbrYguWBGHSt16NFYHo2a5U8WaOBiAi0lB8FgJapdPT9qK1gVvk2LOpj7Z6X5Pagv4067HJTGlqo9X6trOyESIfgotv2mpOfF8sZt-yX6AwIxjzNiE27wq9h2SzjdRZUMS9iIMlXL-ifFyKa73b_3YZP28S9G6Jno2dqBzQGSK1YQISN-L5PeDIvDmgjmEi6mAsTZhJK_p9DNqM8q3zCgeFb-lxym2uQNNEkUxpmKpgI_7afQ61rCAOkjVrG5nX5gUFGtNjyyC41JS4q4lgZTkU0HLzlF5P_Iy2QObpt3AWg0CU5eoeEtGpJHoOvlMfVEHCQLGmX4OQhj08cPz9JbT63H_JodsPY5x0u71x8WaheD3mdOJOtsViecKlN05mETZoHUeubp4Q6sTgOwWSN-8e1H0c7TD0AOdVdttTWZ2ufo7Bziml_5Wr7_t6PhYvtB2XCsBFzcdKhXhMSJX-K5sRwV4YkLcre8y5mWGjW322cNJJGyeePLLah66VsCZ6pAnnFRiy90793cL_UDyD9DQyoUTmmDxMF_eSrCHqbGNuPQ4tte3YItgMJhqCdURH1PI2oi4srIUKnzMkGgAx32lMePd0PWXfin4LU7JCaaKuT1rzLZHozWkaBBLzd3cr0XTJ2Uz5VkDEB2e7ofQDY-v4pKrRLUWvudCM_hASPp9_k9AFHPo9gs5N0J0k4edzyKUgXMXaftMt8zk7Ghpm5QDmUEok9yuxPNDMrA6o-4JZ1xCLTu0PqqDjuMZraf_iGZ4UFwjDWHiUpEQOW4KeeBqUZ-8bvAPtEtiYmG9f5608C__SOfYhmbkIuHqFalplO2AL0sRhv_3ODnv4UtRpCrU8JAbyWj4PWuZIsD4ieKGT-r5BaDcjOakdSatncAc7cy_CHaddLcl8Ou2BLRSIf0_K7PFwAhgI_XyLgGLcPXefrd6WfAhi0U5CKBLGuX3Fq2UXTNTDhhFGcJZjqQcFofvTNHv6FgHTD2SRfOebCKVzv-bz6_HxyzSsEUM0aw.ojcrItYyVFriAqDBzSsLcg'''

    def __init__(self, prompt_prefix, prompt_suffix, annotator_name=None):
        super().__init__(prompt_prefix, prompt_suffix, annotator_name)
        from pychatgpt import ChatGPT
        self.agent = ChatGPT(ChatGPTWebAnnotator.SESSION_TOKEN)

    @timeout_decorator.timeout(16)
    def _call_model_timeout(self, content):
        response = self.agent.send_message(content)
        return response["message"]

    def call_model(self, content, retry=3):

        if retry == 0:
            return None

        try:
            raw_result = self._call_model_timeout(content)
        except timeout_decorator.TimeoutError as e:
            print(f"restarting for time out:{e}")
            from pychatgpt import ChatGPT
            self.agent.__del__()
            del self.agent
            self.agent = ChatGPT(ChatGPTWebAnnotator.SESSION_TOKEN)
            raw_result = self.call_model(content, retry - 1)
        except Exception as e:
            print(f"ChatGPTWeb Wrapper error:{e}")
            raw_result = None

        return raw_result


if __name__ == "__main__":
    from annotator import ModelAnnotator

    prompt_prefix = '''下面的例子都是关于游戏对局中AI机器人数量的讨论

bizim yakındığımız kısım bot sayısı değil

Xingyao 2 sıralı insan -bilgisayar eşleşen sürenin eşleşen süresini kısaltabilir, Angela Suncai Cai Wenji becerileri, nasıl gizlendiğimi gösteren balistik yok mu? Umarım bu oyun uzun süre daha taşınabilir olabilir, cilt çok şişirilmiş, yükleme çok yavaş ve şimdi birkaç şey var.

Haklısın ama kahramanları alıp, onlara göre kabiliyetlerini dizip, derecelide denemek ve karşıda bot olmadan kahramanların sınırlarını, takım savaşı becerilerini, duo complarını vb. şeyleri denememiz gerekmez mi?

Bot gelmesinin sebebi şuanda aktif olarak liginizin eşleşme dercesinde aktif oynayan eşleşme arayan kişilerle eşleşiyorsunuz genelde aktif oynayan kimse yoksa oyununuza botlar atıyor

请根据上面的例子，判断下面的句子是否是AI机器人数量的讨论，请给出原"'''
    prompt_suffix = '''"'''
    annotator = ModelAnnotator.create_annotator(prompt_prefix, prompt_suffix, "ChatGPT")
    api_key = ""
    annotator.set_api_key(api_key)

    content = '''re there many bots in hok or is it just me, I feel like there are bots even though I'm gold 3'''

    result = annotator.annotate(content)
    print(result)
