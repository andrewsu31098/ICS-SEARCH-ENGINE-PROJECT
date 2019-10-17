from collections import defaultdict
from bs4 import BeautifulSoup
from tokenizer import Tokenizer
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
import math
import json

class IIndexBuilder:

    def __init__(self, data_of_docs):
        self.docs_data = data_of_docs
        self.iindex = defaultdict(lambda: defaultdict(float)) 
        self.df_by_token = defaultdict(int)
        self.total_docs = len(self.docs_data) 

        self.docMagnitudes = defaultdict(float)

    def _analyze_doc(self, doc_data):

        bs = BeautifulSoup(doc_data['content'], features = 'lxml')
        tokenizer = Tokenizer()
        tokenizer.tokenize(bs.get_text())
        tokens_dict = tokenizer.get_tokens_dict()

        for token in tokens_dict:
            self.df_by_token[token] += 1
            self.iindex[token][doc_data['id']] = 1 + math.log10(tokens_dict[token]) 

    def build_iindex(self):
        for doc_data in self.docs_data:
            self._analyze_doc(doc_data)

        for token in self.iindex:
            idf = math.log10(self.total_docs / self.df_by_token[token])
            for doc in self.iindex[token]:
                tfIDF = self.iindex[token][doc] * idf 
                self.iindex[token][doc] = tfIDF 
                self.docMagnitudes[doc] += tfIDF * tfIDF 

        for doc in self.docMagnitudes:
            self.docMagnitudes[doc] = math.sqrt(self.docMagnitudes[doc])

    def normalize(self):
        for token in self.iindex: 
            for doc in self.iindex[token]:
                if self.docMagnitudes[doc] != 0:
                    self.iindex[token][doc] = self.iindex[token][doc]/self.docMagnitudes[doc]
        self.docMagnitudes = defaultdict(lambda:1)

    def create_iindex_file(self):
        with open('invertedindex.json', 'w') as the_file:
            json.dump(self.iindex, the_file, indent = 4, sort_keys = True)

    def create_df_file(self):
        with open('df.json','w') as the_file:
            json.dump(self.df_by_token, the_file, indent = 4, sort_keys = True)

    def create_totaldocs_file(self):
        with open('total_docs.txt','w') as the_file:
            the_file.write(str(self.total_docs))