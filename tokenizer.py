from collections import defaultdict
import sys
import re

class Tokenizer:

    def __init__(self):
        self._pattern = re.compile(r'[a-zA-Z0-9]+')
        self._tokens_dict = defaultdict(int)

    def get_tokens_dict(self):
        return self._tokens_dict

    def tokenize(self, text):
        tokens = self._pattern.findall(text)
        for token in tokens:
            token = token.lower()
            self._tokens_dict[token] += 1