from __future__ import (
    unicode_literals, division, print_function, absolute_import)

# built in modules
import os
import sys
import datetime
from six.moves import xrange

# installed modules
import spacy
from unidecode import unidecode

# project modules
try:
    import tools
    import load
except ImportError:
    from . import tools
    from . import load

class duplicate(object):
    def __init__(
            self, solor_fp,
            overlapping_criteria='score', threshold=0.7, window=5,
            similarity_name='jaccard', min_match_length=3,
            verbose=False):

        self.verbose = verbose
        #ontology=['loinc','snomed']
        valid_criteria = {'length', 'score'}
        err_msg = (
            '"{}" is not a valid overlapping_criteria. Choose '
            'between {}'.format(
                overlapping_criteria, ', '.join(valid_criteria)
            )
        )
        assert overlapping_criteria in valid_criteria, err_msg
        self.overlapping_criteria = overlapping_criteria

        valid_similarities = {'dice', 'jaccard', 'cosine', 'overlap'}
        err_msg = ('"{}" is not a valid similarity name. Choose between '
                   '{}'.format(similarity_name, ', '.join(valid_similarities)))
        assert not(valid_similarities in valid_similarities), err_msg
        self.similarity_name = similarity_name

        simstring_fp = os.path.join(solor_fp, 'dup-simstring.db')
        id_fp = os.path.join(solor_fp, 'dupids.db')#change to id based on if


        self.valid_punct = load.UNICODE_DASHES
        self.negations = load.NEGATIONS

        self.window = window
        self.ngram_length = 3
        self.threshold = threshold
        self.min_match_length = min_match_length
        self.to_lowercase_flag = os.path.exists(
            os.path.join(solor_fp, 'lowercase.flag')
        )
        self.normalize_unicode_flag = os.path.exists(
            os.path.join(solor_fp, 'normalize-unicode.flag')
        )

        self._info = None

        #self.accepted_semtypes = accepted_semtypes

        self.ss_db = tools.SimstringDBReader(
            simstring_fp, similarity_name, threshold
        )
        self.ID_db = tools.IDDB(id_fp)
        self.nlp = spacy.load('en')

    def get_all_dups(self,text):
        matches = []
        ss_db=self.ss_db
        ID_db=self.ID_db

        cid,mem,st_dt,ed_dt,npit,pymt,cd = text.split('/')

        text2 = mem + '/' + st_dt + '/' + ed_dt + '/' + npit + '/' + pymt + '/' + cd

        text_norm = text2
        if self.normalize_unicode_flag:
            text_norm = unidecode(text2)

        if self.to_lowercase_flag:
            text_norm = text_norm.lower()



        prev_id = None
        text_cands = list(ss_db.get(text_norm))

        text_matches = []

        for match in text_cands:
            mem_id,start_dt,end_dt,npi,payment,code = match.split('/')
            id_match = sorted(ID_db.get(match))
            #print(id_match,match)


            for id in id_match:
                match_similarity = tools.get_similarity(x=text_norm,y=match,n=self.ngram_length,similarity_name=self.similarity_name)
                if prev_id is not None and prev_id == id:
                    if match_similarity > text_matches[-1]['similarity']:
                        text_matches.pop(-1)
                    else:
                        continue

                prev_id = id

                #mem_id,start_dt,end_dt,npi,payment,code = term.split('/')

                if mem==mem_id and st_dt==start_dt and cd==code and id!=cid:

                    text_matches.append(
                        {
                            'current_clm':text,
                            'term':match,
                            'claim_id':id,
                            'member_id':mem_id,
                            'dos_start_dt':start_dt,
                            'dos_end_dt':end_dt,
                            'npi':npi,
                            'paid_amt':payment,
                            'procedure_code':code,
                            'duplicate':'dup',
                            'similarity':match_similarity
                        }
                    )

        if len(text_matches) > 0:
            matches.append(
                sorted(text_matches, key=lambda m: m['similarity'], reverse=True
                )
            )

        return matches

    def match(self, text, best_match=True, ignore_syntax=False):

        matches = self.get_all_dups(text)
        return matches
