###usage python main_implement.py########

import spacy
import pandas as pd
nlp = spacy.load('en')
import sys
sys.path.append('/home/selineni/Desktop/duplicate')
from main_mod import duplicate
tagger = duplicate('/home/selineni/Desktop/duplicate/output')

df = pd.read_csv('duplicate_file_check.csv')
t=[]
t= df['term']

data=[]

for text in t:
    matches= tagger.match(text,best_match=True, ignore_syntax=False)

    print(matches)

    for match in matches:
        claim = ''
        dup = ''
        dup_claim_id = ''
        member_id = ''
        dos_start_dt = ''
        dos_end_dt = ''
        npi = ''
        paid_amt = ''
        procedure_code = ''
        cid=''
        mem=''
        st_dt=''
        ed_dt=''
        npit=''
        pymt=''
        cd=''
        mi=0
        for m in match:

            #if m['similarity']>mi:
            claim= m['current_clm']
            cid,mem,st_dt,ed_dt,npit,pymt,cd = claim.split('/')
            #cid,'','','','','','' = claim.split('/')
            dup = m['term']
            dup_claim_id = m['claim_id']
            member_id = m['member_id']
            dos_start_dt = m['dos_start_dt']
            dos_end_dt = m['dos_end_dt']
            npi = m['npi']
            paid_amt = m['paid_amt']
            procedure_code = m['procedure_code']
            mi=m['similarity']

            tmp=[]
            tmp.append(cid)
            tmp.append(dup_claim_id)
            tmp.append(member_id)
            tmp.append(dos_start_dt)
            tmp.append(dos_end_dt)
            tmp.append(npi)
            tmp.append(paid_amt)
            tmp.append(procedure_code)
            tmp.append(mi)

            data.append(tmp)

df_matches = pd.DataFrame(data=data, columns =['claim','dup_claim_id','member_id','dos_start_dt','dos_end_dt','npi','paid_amt','procedure_code','similarity'])
#print(df_matches)
df_matches.to_csv('duplicate_out.csv',index=False)
    #print(df_matches["term"])'''
