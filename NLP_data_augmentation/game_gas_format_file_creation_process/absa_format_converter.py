import inspect
import os.path
import re
from tqdm import tqdm
import json

NULL = "<NULL>"
def get_tokens2char_offsets(tokens):
    l = len(tokens)
    token_lens = list(map(lambda t: len(t), tokens))
    token_begin_char_offset = [0] * l
    token_end_char_offset = [0] * l
    token_end_char_offset[0] = token_lens[0]
    for i in range(1, l):
        token_begin_char_offset[i] = token_begin_char_offset[i - 1] + token_lens[i - 1] + 1
        token_end_char_offset[i] = token_begin_char_offset[i] + token_lens[i]

    tokens2char_offsets = list(zip(token_begin_char_offset, token_end_char_offset))
    return tokens2char_offsets


def boundary_char2token(tokens2char_offsets, boundary_char):
    token_offset = [None, None]
    for i, (b_char, e_char) in enumerate(tokens2char_offsets):
        if b_char <= boundary_char[0] <= e_char:
            token_offset[0] = i

        if b_char <= boundary_char[1] <= e_char:
            token_offset[1] = i + 1

    return token_offset


def ssa_parse2dict(quad_raw_dict, key, tokens2char_offsets):
    span_info = quad_raw_dict[key]
    if len(span_info[0]) == 0:
        span_dict = {
            "content": NULL,
            "token_start": -1,
            "token_end": -1,
        }
        return span_dict

    span_content = span_info[0][0]
    span_charoffset = span_info[1][0].split(":")
    span_charoffset = list(map(lambda x: int(x), span_charoffset))
    span_tokenoffset = boundary_char2token(tokens2char_offsets, span_charoffset)

    span_dict = {
        "content": span_content,
        "token_start": span_tokenoffset[0],
        "token_end": span_tokenoffset[1],
    }

    return span_dict

def textRemoveNumbersAndSymbols(string:str):
    result = "".join(filter(lambda x: not x.isdigit(), string))
    result = re.sub(r'[^\w]', '', result)
    return result


class ABSAFormatLoadFuncs:
    SentimentMap = {
        "POS": "Positive",
        "NEG": "Negative",
        "NEU": "Neutral",
    }

    @staticmethod
    def ssa(input_data):
        sent = input_data["text"]
        tokens = sent.split()

        tokens2char_offsets = get_tokens2char_offsets(tokens)

        state = {
            "tokens": tokens,
            "sentence": sent,
            "quads": [],
        }

        quads = []
        for quad_raw_dict in input_data["opinions"]:
            category = None

            holder = ssa_parse2dict(quad_raw_dict, "Source", tokens2char_offsets)

            aspect = ssa_parse2dict(quad_raw_dict, "Target", tokens2char_offsets)

            opinion = ssa_parse2dict(quad_raw_dict, "Polar_expression", tokens2char_offsets)

            sentiment = quad_raw_dict["Polarity"]

            intensity = quad_raw_dict["Intensity"]

            quad = {
                "category": category,
                "aspect": aspect,
                "opinion": opinion,
                "sentiment": sentiment,
                "holder": holder,
                "intensity": intensity,
            }

            quads.append(quad)

        state["quads"] = quads
        return state

    @staticmethod
    def gas(input_data, sep="####"):
        sent, triplets = input_data.split(sep)
        tokens = sent.split()

        state = {
            "tokens": tokens,
            "sentence": sent,
            "quads": [],
        }

        triplets = eval(triplets)
        quads = []
        for a, o, sentiment in triplets:
            category = None
            aspect = {
                "content": ' '.join(tokens[a[0]: a[-1] + 1]),
                "token_start": a[0],
                "token_end": a[-1] + 1,
            }

            opinion = {
                "content": ' '.join(tokens[o[0]: o[-1] + 1]),
                "token_start": o[0],
                "token_end": o[-1] + 1,
            }

            sentiment = ABSAFormatLoadFuncs.SentimentMap[sentiment]

            quad = {
                "category": category,
                "aspect": aspect,
                "opinion": opinion,
                "sentiment": sentiment,
            }

            quads.append(quad)

        state["quads"] = quads

        return state

    @staticmethod
    def quad(input_data):
        '''
        Quad
        The food is very average ... the Thai fusion stuff is a bit too sweet , every thing they serve is too sweet here .####[["food", "NULL", "negative", "average"], ["Thai fusion", "NULL", "negative", "too sweet"]]

        :param input_data:
        :return:
        '''
        sent, quads_list = input_data.split("####")
        tokens = sent.split()

        state = {
            "tokens": tokens,
            "sentence": sent,
            "quads": [],
        }

        quads = []
        for quad_arr in eval(quads_list):
            category = quad_arr[0]
            aspect = {
                "content": quad_arr[1],
                "token_start": -1,
                "token_end": -1
            }

            opinion = {
                "content": quad_arr[3],
                "token_start": -1,
                "token_end": -1
            }

            sentiment = quad_arr[2]

            quad = {
                "category": category,
                "aspect": aspect,
                "opinion": opinion,
                "sentiment": sentiment,
            }

            quads.append(quad)

        return state

    @staticmethod
    def game(input_data):
        state = json.loads(input_data.rstrip())
        triplets = state["triplets"]
        del state["triplets"]
        quads = []

        for triplet in triplets:
            quad = triplet
            quad["category"] = None
            quads.append(quad)

        state["quads"] = quads
        return state

    @staticmethod
    def spanaste(input_data):
        return ABSAFormatLoadFuncs.gas(input_data, sep="#### #### ####")


class ABSAFormatDumpFuncs:
    no_duplicate = False

    SentimentMap = {
        "positive": "POS",
        "negative": "NEG",
        "bad": "NEU",
        "neutral": "NEU",
    }

    @staticmethod
    def gas(state, sep="####"):
          '''
          GAS format
          In the shop , these MacBooks are encased in a soft rubber enclosure - so you will never know about the razor edge until you buy it , get it home , break the seal and use it ( very clever con ) .####[([11, 12], [10], 'POS')]

          :param state:
          :return:
          '''
          tokens = state["tokens"]
          if state["sentence"].startswith("Like the title says"):
              print()

          tokens = ["<SPACE>" if t.isspace() else t for t in tokens]
          tokenized_sent = ' '.join(tokens)
          quads = []
          quads_set = set()
          for quad in state["quads"]:
            try:
                aspect = quad["aspect"]
                opinion = quad["opinion"]
                sentiment = quad["sentiment"]

                if "token_start" in aspect and "token_end" in aspect:
                  aspect_pos = [aspect["token_start"], aspect["token_end"] - 1]
                else:
                  aspect_pos = [0,0]
                
                if aspect_pos[0] == aspect_pos[1]:
                    aspect_pos = [aspect_pos[0]]
                
                if aspect == '':
                  aspect = {}
                  aspect['content'] = NULL
                elif aspect == {}:
                  aspect["content"] = NULL
                
                if_aspect_null = aspect["content"] == NULL or any([e == -1 for e in aspect_pos])
                if if_aspect_null:
                    aspect_pos = [len(tokens)]
                else:
                    if len(aspect_pos) > 1 and aspect_pos[1] <= aspect_pos[0]:
                        # print()
                        aspect_pos = [aspect_pos[0]]

                if "token_start" in opinion and "token_end" in opinion:
                  opinion_pos = [opinion["token_start"], opinion["token_end"] - 1]
                else:
                  opinion_pos = [0,0]
                
                if opinion_pos[0] == opinion_pos[1]:
                    opinion_pos = [opinion_pos[0]]

                if opinion == {}:
                  opinion['content'] = NULL
                if_opinion_null = opinion["content"] == NULL or any([e == -1 for e in opinion_pos])
                if if_opinion_null:
                    opinion_pos = [len(tokens)]
                else:
                    if len(opinion_pos) > 1 and opinion_pos[1] <= opinion_pos[0]:
                        # print()
                        opinion_pos = [opinion_pos[0]]

                sentiment = sentiment.lower()

                triplet = (aspect["content"], opinion["content"], sentiment)
                if triplet in quads_set:
                    continue

                quads_set.add(triplet)
                
                if textRemoveNumbersAndSymbols(sentiment) in ABSAFormatDumpFuncs.SentimentMap:  # and not if_aspect_null and not if_opinion_null:
                    sentiment = ABSAFormatDumpFuncs.SentimentMap[textRemoveNumbersAndSymbols(sentiment)]
                    quad = (aspect_pos, opinion_pos, sentiment)
                    quads.append(quad)
                else:
                  print(f"Unknown sentiment {sentiment} in {quad}\n{tokenized_sent}")
                  continue
                  raise Exception(f"Unknown sentiment {sentiment} in {quad}\n{tokenized_sent}")
            except Exception as e:
              print(e)
          output = f"{tokenized_sent}{sep}{quads}"
          return output

    @staticmethod
    def quad(state):
        '''
        The food is very average ... the Thai fusion stuff is a bit too sweet , every thing they serve is too sweet here .####[["food", "NULL", "negative", "average"], ["Thai fusion", "NULL", "negative", "too sweet"]]

        :param state:
        :return:
        '''
        tokens = state["tokens"]
        tokenized_sent = ' '.join(tokens)
        quads = []
        for quad in state["quads"]:
            category = quad["category"]

            if category == NULL or category is None:
                category = "NULL"

            aspect = quad["aspect"]
            opinion = quad["opinion"]
            sentiment = quad["sentiment"]

            if_aspect_null = aspect["content"] == NULL or aspect["content"] is None
            if_opinion_null = opinion["content"] == NULL or opinion["content"] is None

            sentiment = sentiment.lower()
            quad = [aspect["content"], category, sentiment, opinion["content"]]
            quads.append(quad)

        output = f"{tokenized_sent}####{quads}"
        return output

    @staticmethod
    def game(state):
        quads = state["quads"]
        del state["quads"]
        state["triplets"] = quads
        output = json.dumps(quads)
        return output

    @staticmethod
    def spanaste(state):
        return ABSAFormatDumpFuncs.gas(state, sep="#### #### ####")

    @staticmethod
    def bartabsa(state):

        '''
        state Format
        "quads": [
        {
          "opinion": {
            "content": "issues",
            "token_start": 10,
            "token_end": 11
          },
          "aspect": {
            "content": "optimization",
            "token_start": 9,
            "token_end": 10
          },
          "sentiment": "Negative"
        }
        ]

        bartabsa format
        https://github.com/yhcc/BARTABSA/
         "aspects": [
          {
            "index": 0,
            "from": 4,
            "to": 6,
            "polarity": "POS",
            "term": [
              "proprietary",
              "software"
            ]
          }
        ],
        "opinions": [
          {
            "index": 0,
            "from": 3,
            "to": 4,
            "term": [
              "excellent"
            ]
          }
        ]

        :param state:
        :return:

        '''

        aspects = []
        opinions = []

        for idx, triplet in enumerate(state["quads"]):
            aspect = {
                "index": idx,
                "from": triplet["aspect"]["token_start"],
                "to": triplet["aspect"]["token_end"],
                "polarity": ABSAFormatDumpFuncs.SentimentMap[triplet["sentiment"].lower()],
                "term": triplet["aspect"]["content"].split(" ")
            }

            opinion = {
                "index": idx,
                "from": triplet["opinion"]["token_start"],
                "to": triplet["opinion"]["token_end"],
                "term": triplet["opinion"]["content"].split(" ")
            }

            aspects.append(aspect)
            opinions.append(opinion)

        output = {
            "raw_words": " ".join(state["tokens"]),
            "words": state["tokens"],
            "aspects": aspects,
            "opinions": opinions,
        }
        # output = json.dumps(output)
        return output

    @staticmethod
    def uie(state):

        '''
        state Format
        "quads": [
        {
          "opinion": {
            "content": "issues",
            "token_start": 10,
            "token_end": 11
          },
          "aspect": {
            "content": "optimization",
            "token_start": 9,
            "token_end": 10
          },
          "sentiment": "Negative"
        }
        ]

        bartabsa format
        https://github.com/yhcc/BARTABSA/
         "aspects": [
          {
            "index": 0,
            "from": 4,
            "to": 6,
            "polarity": "POS",
            "term": [
              "proprietary",
              "software"
            ]
          }
        ],
        "opinions": [
          {
            "index": 0,
            "from": 3,
            "to": 4,
            "term": [
              "excellent"
            ]
          }
        ]

        :param state:
        :return:

        '''

        aspects = []
        opinions = []
        l = len(state["tokens"])

        for idx, triplet in enumerate(state["quads"]):

            s, e = triplet["aspect"]["token_start"], triplet["aspect"]["token_end"]
            term = triplet["aspect"]["content"].split(" ")
            if s == e == -1:
                s, e = l, l + 1
                term = ""

            aspect = {
                "index": idx,
                "from": s,
                "to": e,
                "polarity": ABSAFormatDumpFuncs.SentimentMap[triplet["sentiment"].lower()],
                "term": term,
            }

            s, e = triplet["opinion"]["token_start"], triplet["opinion"]["token_end"]
            term = triplet["opinion"]["content"].split(" ")
            if s == e == -1:
                s, e = l, l + 1
                term = ""

            opinion = {
                "index": idx,
                "from": s,
                "to": e,
                "term": term,
            }

            aspects.append(aspect)
            opinions.append(opinion)

        output = {
            "raw_words": " ".join(state["tokens"]),
            "words": state["tokens"],
            "aspects": aspects,
            "opinions": opinions,
        }
        # output = json.dumps(output)
        return output

    @staticmethod
    def triplet(state):

        l = len(state["tokens"])

        triplets = []

        for idx, triplet in enumerate(state["quads"]):

            s, e = triplet["aspect"]["token_start"], triplet["aspect"]["token_end"]
            term = triplet["aspect"]["content"]
            if s == e == -1:
                s, e = l, l + 1
                term = ""

            aspect = term

            s, e = triplet["opinion"]["token_start"], triplet["opinion"]["token_end"]
            term = triplet["opinion"]["content"]
            if s == e == -1:
                s, e = l, l + 1
                term = ""

            opinion = term
            triplets.append((aspect, opinion, triplet["sentiment"].lower()))

        output = {
            "sent": ' '.join(state["tokens"]),
            "triplets": triplets
        }

        return triplets


class ABSAFormatConvert:
    load_funcs = {
        name: func for name, func in inspect.getmembers(ABSAFormatLoadFuncs, predicate=inspect.isfunction)
    }

    dump_funcs = {
        name: func for name, func in inspect.getmembers(ABSAFormatDumpFuncs, predicate=inspect.isfunction)
    }

    file_formats = {
        "bartabsa": "json",
        "gas": "txt",
        "quad": "txt",
        "game": "txt",
        "spanaste": "txt",
        "uie": "json",
        "ssa": "json",
    }

    def __init__(self, from_format: str, to_format: str):
        self.from_format = from_format
        self.to_format = to_format

        self.input_format = ABSAFormatConvert.file_formats[self.from_format]
        self.output_format = ABSAFormatConvert.file_formats[self.to_format]

        self.load = self.load_funcs[from_format]
        self.dump = self.dump_funcs[to_format]

        self.convert2format_funcs = {
            "txt": self.convert2txt,
            "json": self.convert2json,
            # "csv": self.convert2csv,
        }

        self.convert_from_format_funcs = {
            "json": self.convert_from_json,
            "txt": self.convert_from_txt,
        }

        self.convert_from_format = self.convert_from_format_funcs[self.input_format]
        self.convert2format = self.convert2format_funcs[self.output_format]

        print(
            f"Intialized convert with format {self.from_format} to {self.to_format} with {self.input_format} to {self.output_format}")

    def convert(self, input_data):
        state = self.load(input_data)
        output_data = self.dump(state)
        return output_data

    def convert2txt(self, input_path: str, output_path: str):
        print(f"Convert {input_path} in {self.from_format} format to {output_path} in {self.to_format} format...")
        with open(input_path) as fin, open(output_path, "w") as fout:
            for line_idx, input_data in tqdm(enumerate(fin)):
                input_data = input_data.rstrip()
                output_data = self.convert(input_data)
                fout.write(output_data + '\n')
        print(f"Completed")

    def convert2json(self, input_path: str, output_path: str):
        print(f"Convert {input_path} in {self.from_format} format to {output_path} in {self.to_format} format...")
        outputs = []
        with open(input_path) as fin, open(output_path, "w") as fout:
            for line_idx, input_data in tqdm(enumerate(fin)):
                input_data = input_data.rstrip()
                output_data = self.convert(input_data)
                outputs.append(output_data)
            fout.write(json.dumps(outputs, indent=4))
        print(f"Completed")

    def convert_from_json(self, input_path: str):
        for input_data in json.load(open(input_path)):
            yield self.load(input_data)

    def convert_from_txt(self, input_path: str):
        with open(input_path) as fin:
            for line_idx, input_data in tqdm(enumerate(fin)):
                yield input_data.rstrip()

    def convertX2Y(self, input_path: str, output_path: str):
        print(f"Convert {input_path} in {self.from_format} format to {output_path} in {self.to_format} format...")
        if self.output_format not in self.convert2format_funcs:
            raise Exception(f"Unsupported output_format:{self.output_format}")
        outputs = []
        with open(output_path, "w") as fout:
            for state in self.convert_from_format(input_path):
                state = self.load(state)
                output_data = self.dump(state)
                outputs.append(output_data)

            if self.output_format == "txt":
                fout.write('\n'.join(outputs) + '\n')
            elif self.output_format == "json":
                json.dump(outputs, fout, indent=4)
        print(f"Completed")

    def convert2csv(self, input_path: str, output_path: str):
        NotImplemented

    def convert_splits(self, version: str, dataset_dir: str, splits=["train", "valid", "test"]):
        input_dir = f'{dataset_dir}_{version}'
        output_dir = os.path.join(input_dir, f"{self.to_format}")
        os.makedirs(output_dir, exist_ok=True)

        if self.from_format != "game":
            input_dir = os.path.join(input_dir, self.from_format)

        print(f"Convert dataset in {input_dir} with format {self.from_format} to {self.to_format} on splits {splits}")

        for split in splits:
            input_path = os.path.join(input_dir, f"{split}.{self.input_format}")
            output_path = os.path.join(output_dir, f"{split}.{self.output_format}")
            self.convertX2Y(input_path, output_path)  # self.convert2format(input_path, output_path)

