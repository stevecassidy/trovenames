import nltk

MULTICLASS_NE_CHUNKER = 'chunkers/maxent_ne_chunker/english_ace_multiclass.pickle'

def chunker():
    """Return an instance of ne_chunker by loading a stored model"""

    return nltk.load(MULTICLASS_NE_CHUNKER)


def prepare(text):
    """Prepare a text for NER, return a list of 
    list of POS tagged tokens (one list per sentence)."""
    
    # tokenize
    tokens = []
    sentences = nltk.sent_tokenize(text)
    for sent in sentences:
        words = nltk.word_tokenize(sent)
        tokens.append(words)
    
    # pos tag
    postags = []
    for sent in tokens:
        tags = nltk.pos_tag(sent)
        postags.append(tags)
    
    return postags
    
    
def prepare_nosent(tokens):
    """Prepare a list of tokens with no sentence markers
    for NER - return a list of tokens with POS tags"""

    return nltk.pos_tag(tokens)


def read_conll(fname):
    """Read a CONLL file, return a list of tokens"""

    with open(fname) as fd:
        tokens = []
        conll = []
        for line in fd.readlines():
            (tok, tag) = line.split()
            tokens.append(tok)
            conll.append((tok, tag))
    return tokens     
    return " ".join(tokens)

if __name__=='__main__':
    
    text = read_conll('dev_50_conll/106916808.conll')
    #text = "My name is Steve Cassidy and I live in Sydney, Australia. Who is Malcolm Fraser?"
    
    postagged = prepare_nosent(text)
    
    print(postagged)
    
    chunker = chunker()
    
    ne = chunker.parse(postagged)
    
    # print the results in CONLL format
    print(nltk.chunk.util.tree2conllstr(ne))
    
    # evaluate against itself - expect 100%
    print(chunker.evaluate([ne]))

        
        