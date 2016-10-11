#!/usr/local/bin/python

from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def input():
    return render_template('input.html')

def produce_coocs(text):
    """
    """
    
    fdist = nltk.probability.ConditionalFreqDist()
    
    # first split into sentences
    lines = nltk.tokenize.line_tokenize(text.lower())
    foo = [nltk.tokenize.sent_tokenize(line) for line in lines]
    sents = [item for sublist in foo for item in sublist]

    # catalog co-occurrences within each sentence
    for sent in sents:
        tokens = nltk.tokenize.wordpunct_tokenize(sent)
        
        # now catalog co-occurrences within each sentenc
        for t in range(0, len(tokens)):
            tok = tokens[t]
            if not unicode.isalnum(tok) or tok in nltk.corpus.stopwords.words('english'):
                continue
        
            # get everything within a 4-gram window
            for i in range(1,5):
                if t + i < len(tokens):
                    other = tokens[t + i]
                    if not unicode.isalnum(other) or\
                            other in nltk.corpus.stopwords.words('english') or tok == other:
                        continue
                    # ensure alpha order. first is the condition.
                    if tok < other:
                        fdist[tok].inc(other, 1.0 / i)
                    else:
                        fdist[other].inc(tok, 1.0 / i)
    
    return fdist

def dump_coocs_to_json(text, coocs, filename='coocs.json'):
    """
    @param coocs: Conditional frequency distribution as returned by produce_coocs.
    """
    
    data = {}
    
    top_n = 100
    
    # put in the text, replacing carriage returns with <BR>'s
    #data['text'] = text.replace('\n', '<BR><BR>')
    lines = nltk.tokenize.line_tokenize(text)
    data['sents'] = []
    for line in lines:
        # foo = [nltk.tokenize.sent_tokenize(line) for line in lines]
        # sents = [item for sublist in foo for item in sublist]
        sents = nltk.tokenize.sent_tokenize(line)
        # data['sents'] = [{'sent': '', 'words': []}]
        for sent in sents:
            tokens = nltk.tokenize.wordpunct_tokenize(sent.lower())
            data['sents'].append({'sent': sent, 'words': tokens})
        data['sents'].append({'sent': "<BR><BR>", 'words': ''})
    
    # first, figure out all the node names and frequencies
    tokens = nltk.tokenize.wordpunct_tokenize(text.lower())
    tokens = [t for t in tokens 
            if t[0] and unicode.isalnum(t) 
            and not unicode.isnumeric(t)
            and t not in nltk.corpus.stopwords.words('english')
            and len(t) > 2]
    fdist = nltk.probability.FreqDist(tokens)
    data['nodes'] = []
    for t in fdist.samples()[0:top_n]:
        data['nodes'].append({'name': t, 'value': fdist[t]})
    
    # now add edges for the co-occurrence data
    data['links'] = []
    for condition in coocs:
        if condition not in fdist.samples()[0:top_n]:
            continue
        for word, weight in coocs[condition].items():
            if word not in fdist.samples()[0:top_n]:
                continue
            data['links'].append({'source': fdist.samples().index(condition), 
                    'target': fdist.samples().index(word), 'value': weight})
    
    # write the output file
    outfile = io.open(filename, 'w', encoding='utf-8')
    outfile.write(json.dumps(data, ensure_ascii=False))
    outfile.close()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

    
