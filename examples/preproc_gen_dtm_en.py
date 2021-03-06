"""
An example for preprocessing documents in English language and generating a document-term-matrix (DTM).
"""
from pprint import pprint
from tmtoolkit.preprocess import TMPreproc

import pandas as pd


if __name__ == '__main__':   # this is necessary for multiprocessing on Windows!
    corpus = {
        'doc1': 'A simple example in simple English.',
        'doc2': 'It contains only three very simple documents.',
        'doc3': 'Simply written documents are very brief.',
    }

    preproc = TMPreproc(corpus, language='english')

    print('input corpus:')
    pprint(corpus)

    print('running preprocessing pipeline...')
    preproc.tokenize().pos_tag().lemmatize().tokens_to_lowercase().clean_tokens()

    print('final tokens:')
    pprint(preproc.tokens)

    print('DTM:')
    doc_labels, vocab, dtm = preproc.get_dtm()

    # using pandas just for a nice tabular output
    print(pd.DataFrame(dtm.todense(), columns=vocab, index=doc_labels))
