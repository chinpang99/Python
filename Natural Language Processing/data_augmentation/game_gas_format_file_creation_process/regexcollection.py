import re

class SocialMediaRegex():
    social_media_username_re = re.compile(r'([#]([A-Za-z0-9_.]+))') #(r'([@#]([A-Za-z0-9_.]+))')
    social_media_event_re = re.compile(r'([#]([A-Za-z0-9_.]+))')
    social_media_username_event_re = re.compile(r'([@#]([A-Za-z0-9_.]+))')
    # emoji_pattern =
    emoji_re = re.compile(
        "(["
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "])"
      )

    url_re = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%_[0-9a-fA-F][0-9a-fA-F]))+')  # 匹配模式

    non_ascii_re = re.compile(r'[^\x00-\x7f]')

    tiktok_special_chars = re.compile(r"{}".format(emoji_re.pattern), re.U)

    french2english = str.maketrans("éàèùâêîôûç", "eaeuaeiouc")
    nonenglishpunct2english = str.maketrans("。，！？‘’“”/", ".,!?''" + '""' + " ")

    @staticmethod
    def replace_nonascii(s:str, target=r' ', replace_nonascii2space=True, replace_french_letter=False, replace_nonenpunc_letter=False):
        if replace_french_letter:
            s = s.translate(SocialMediaRegex.french2english)

        if replace_nonenpunc_letter:
            s = s.translate(SocialMediaRegex.nonenglishpunct2english)

        ret = s

        if replace_nonascii2space:
            ret = re.sub(SocialMediaRegex.non_ascii_re, target, s)

        return ret

    @staticmethod
    def replace_tiktok_special_chars(s: str, target=r' ', replace_french_letter=False):
        ret = s

        #first replace # @ to spaces
        for m in SocialMediaRegex.social_media_username_event_re.finditer(ret):
            start, end = m.span()
            l = end - start
            ret = ret[:start] + ' ' * l + ret[end:]


        #second replace special non-English with english token
        # ret = ret.replace("’", "'")
        # ret = ret.replace('“', '"')
        # ret = ret.replace("”", "'")

        ret = ret.translate(SocialMediaRegex.nonenglishpunct2english)

        if replace_french_letter:
            ret = ret.translate(SocialMediaRegex.french2english)

        #third replace non-English text with spaces
        # ret = re.sub(SocialMediaRegex.emoji_re, target, s)
        ret = re.sub(SocialMediaRegex.non_ascii_re, target, ret)

        return ret


if __name__ == "__main__":
    text = 'How’s to “turn” a taken “women” on part’s， 1。 😅🤣🤣🤣#fyp#imatakenwoman #funny @leodot'
    text = '#edits #likeforlike #love #viral #dėpressiøn #mentalhealth #sad #followme #sadaudio #sadedits #like #foryoupage #ayzcba #foryou #bitemechallenge'
    print('|||' + text  + '|||')
    ret = SocialMediaRegex.replace_tiktok_special_chars(text, replace_french_letter=True)
    print('|||' + ret  + '|||', len(text), len(ret))
