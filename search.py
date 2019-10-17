import json
import math 
import os 
from tokenizer import Tokenizer
from corpus import Corpus
from collections import defaultdict
from bs4 import BeautifulSoup

class SearchEngine:    
    JSON_FILE_NAME = "invertedindex.json"
    DF_FILE_NAME = "df.json"
    TOTALDOCS_FILE_NAME = "total_docs.txt"
    WEBPAGES_RAW_NAME = "WEBPAGES_RAW"

    # BOOKKEEPING_FILE_NAME = os.path.join(".", WEBPAGES_RAW_NAME, "bookkeeping.json")

    def __init__(self):
        self.inverted_index = json.load(open(self.JSON_FILE_NAME), encoding="utf-8")
        self.df_by_token = json.load(open(self.DF_FILE_NAME))
        self.total_docs = int(open(self.TOTALDOCS_FILE_NAME,'r').read())
        self.corpus = Corpus()

        # self.file_url_map = json.load(open(self.BOOKKEEPING_FILE_NAME), encoding="utf-8")

    def search(self, search_query):

        queryTokenizer = Tokenizer()
        queryTokenizer.tokenize(search_query)
        tokens_dict = queryTokenizer.get_tokens_dict()
        
        nonexistent_terms = 0 
        for term in tokens_dict:
            if term not in self.inverted_index:
                nonexistent_terms += 1
        if nonexistent_terms == len(tokens_dict):
            print("No documents found with the search terms")
            return None

        query_magnitude = 0 
        query_vector = defaultdict(float)
        for term in tokens_dict:
            if term not in self.df_by_token:
                tfIDF = 0 
            else:
                tfIDF = (1 + math.log10(tokens_dict[term])) * (math.log10(self.total_docs/self.df_by_token[term]))
            query_vector[term] = tfIDF 
            query_magnitude += tfIDF * tfIDF 
        query_magnitude = math.sqrt(query_magnitude)

        for term in tokens_dict:
            if query_magnitude != 0:
                query_vector[term] /= query_magnitude 

        score_dict = defaultdict(float)
        for queryToken in query_vector:
            if queryToken not in self.inverted_index:
                continue 
            for docID in self.inverted_index[queryToken]:
                # print(docID)
                score_dict[docID] += query_vector[queryToken] * self.inverted_index[queryToken][docID]

        numResults = 0 
        results = [] 
        allSearchResults = sorted(score_dict.items(),key = lambda docAndScore: docAndScore[1], reverse = True)
        for docID,score in allSearchResults:
            if numResults < 20:
                # print("DocID: {} \n URL: {} \n Score:{} \n".format(docID, self.corpus.get_url(docID),score))

                url = self.corpus.get_url(docID)
                title = ''
                the_file = self.corpus.get_file_name_without_scheme(url)
                
                with open(the_file, mode = 'rb') as open_file:
                    bs = BeautifulSoup(open_file.read(), features = 'lxml')
                    if bs.title == None:
                        title += "No description available for this page"
                    else:
                        title += bs.title.get_text()

                results.append((url,title))
            numResults += 1

        # print("Total Number of Results for: \n{}\n{}\n\n".format(search_query,numResults))
        return results 
    

