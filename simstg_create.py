from __future__ import unicode_literals, division, print_function

# built in modules
import os
import sys
import time
import codecs
import shutil
import argparse
from six.moves import input

# project modules
from tools import countlines, IDDB, SimstringDBWriter, mkdir
from load import HEADERS, LANGUAGES

def get_file_iterator(path, headers, lang='ENG'):
    with codecs.open(path, encoding='utf-8') as f:
        for i, ln in enumerate(f):
            content = dict(zip(headers, ln.strip().split(',')))

            yield content


def extract_from_file(file_path,arg,header=HEADERS):
    start = time.time()

    ont_extract = get_file_iterator(file_path,header,arg.language)

    total = countlines(file_path) # i need to add this in tools

    processed = set()
    i=0
    for content in ont_extract:
        i += 1
        if i % 100000 == 0:
            delta = time.time() - start
            status = (
                '{:,} in {:.2f} s ({:.2%}, {:.1e} s / term)'
                ''.format(i, delta, i / total, delta / i if i > 0 else 0)
            )
            print(status)

        concept_text = content['term'].strip()
        id = content['sno']
        '''mem_id = content['mem_id']
        start_dt = content['start_dt']
        end_dt = content['end_dt']
        npi = content['npi']
        payment = content['payment']
        code = content['code']'''

        if arg.lowercase:
            concept_text = concept_text.lower()

        if arg.normalize_unicode:
            concept_text = unidecode(concept_text)

        if (id, concept_text) in processed:
            continue
        else:
            processed.add((id, concept_text))

        yield (concept_text, id)# , mem_id,start_dt,end_dt,npi,payment,code change this accordingly concept_text and id are imp

    '''delta = time.time() - start
    status = (
        '\nCOMPLETED: {:,} in {:.2f} s ({:.1e, is_preferred} s / term)'
        ''.format(i, delta, i / total, delta / i if i > 0 else 0)
    )
    print(status)'''

def parse_and_encode_ngrams(extracted_it, simstring_dir, ids_dir,arg):#check and modyfy
    # Create destination directories for the two databases
    mkdir(simstring_dir)
    mkdir(ids_dir)

    ss_db = SimstringDBWriter(simstring_dir,arg) # here added arg and going to tools
    ids_db = IDDB(ids_dir)

    simstring_terms = set()

    for i, (term, id) in enumerate(extracted_it, start=1):
        if term not in simstring_terms:
            ss_db.insert(term)
            simstring_terms.add(term)

        ids_db.insert(term, id) #,mem_id,start_dt,end_dt,npi,payment,code comeback to here after reviewing main program

def sender(arg):
    if not os.path.exists(arg.destination_path):
        msg = ('Directory "{}" does not exists; should I create it? [y/N] '
               ''.format(arg.destination_path))
        create = input(msg).lower().strip() == 'y'

        if create:
            os.makedirs(arg.destination_path)
        else:
            print('Aborting.')
            exit(1)

    if len(os.listdir(arg.destination_path)) > 0:
        msg = ('Directory "{}" is not empty; should I empty it? [y/N] '
               ''.format(arg.destination_path))
        empty = input(msg).lower().strip() == 'y'
        if empty:
            shutil.rmtree(arg.destination_path)
            os.mkdir(arg.destination_path)
        else:
            print('Aborting.')
            exit(1)

    if arg.normalize_unicode:
        try:
            unidecode
        except NameError:
            err = ('`unidecode` is needed for unicode normalization'
                   'please install it via the `[sudo] pip install '
                   'unidecode` command.')
            print(err, file=sys.stderr)
            exit(1)

        flag_fp = os.path.join(arg.destination_path, 'normalize-unicode.flag')
        open(flag_fp, 'w').close()

    if arg.lowercase:
        flag_fp = os.path.join(arg.destination_path, 'lowercase.flag')
        open(flag_fp, 'w').close()

    flag_fp = os.path.join(arg.destination_path, 'language.flag')
    with open(flag_fp, 'w') as f:
        f.write(arg.language)

    file_path = os.path.join(arg.installation_path, 'duplicate_file.csv')
    file_iterator = extract_from_file(file_path,arg)#need to create this Function

    simstring_dir = os.path.join(arg.destination_path, 'dup-simstring.db')#loinc-simstring.db change to the name of db that we look
    #print(simstring_dir)
    ids_dir = os.path.join(arg.destination_path, 'dupids.db')

    parse_and_encode_ngrams(file_iterator, simstring_dir, ids_dir,arg)

############################################################################################
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument(
        'installation_path',
        help=('Location of Total Claims files')
    )
    ap.add_argument(
        'destination_path',
        help='Location where the necessary files are installed'
    )
    ap.add_argument(
        '-L', '--lowercase', action='store_true',
        help='Consider only lowercase version of tokens'
    )
    ap.add_argument(
        '-U', '--normalize-unicode', action='store_true',
        help='Normalize unicode strings to their closest ASCII representation'
    )
    ap.add_argument(
        '-E', '--language', default='ENG', choices=LANGUAGES,
        help='Extract concepts of the specified language'
    )
    ap.add_argument(
        '-O', '--ontology', default='loinc',
        help='Extract concepts of the specified ontology'
    )
    arg = ap.parse_args()

sender(arg)
