#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Collect nearest words for every item in the word vector model
"""
#TODO: multithreading? unicode strings
#IDEA: what if every word was embedded separately for its every possible pos tag? Like run#VB, run#N?

import argparse
import codecs 
from gensim.models import word2vec
import pbar


def run(model_path, output_path, n=200, vocab_limit=None,
                       model_format='word2vec', binary=True):
    """Collect nearest words for every item in the word vector model

    This function prepares input for the Chinese whispers algorithm. It iterates 
    over all words in a provided word vector model, takes n nearest 
    neighbours of this word based on cosine vector similarity and saves the result 
    to output_path in the following format:
    word1<TAB>neighbour1<TAB>similarity
    ...
    word1<TAB>neighbourN<TAB>similarity
    word2<TAB>neighbour1<TAB>similarity
    ...

    Args:
        model_path: path to a word vector model
        output_path: path to a text file where neighbours are saved
        n: number of nearest neighbours to be collected for each word
        model_format: a format of a word veector model. Choose "word2vec" if 
            your model has been saved in the format of word2vec original implementation.
            Choose "gensim" if your model has been trained with gensim implementation
            of the word2vec program and saved in its format.
        binary: True if your model has been saved in a binary format, False if it has 
            been saved in a text format. Only applies to "word2vec" models.
    """

    print("Loading model from " + model_path)
    if model_format == 'word2vec':
        model = word2vec.Word2Vec.load_word2vec_format(model_path, binary=binary)
    if model_format == 'gensim':
        model = word2vec.Word2Vec.load(model_path)
    vocab_size = len(model.vocab)
    print("Vocabulary size: %i" % vocab_size)
    
    # Limit the number of words for which to collect neighbours
    if vocab_limit and vocab_limit < vocab_size:
        vocab_size = vocab_limit
        
    print("Collect neighbours for %i most frequent words" % vocab_size)
    print("Saving word neighbours to " + output_path)
    
    with codecs.open(output_path, 'w', encoding='utf-8') as output:
        pb = pbar.Pbar(vocab_size, 100)
        pb.start()
        i = 0
        for word in model.index2word[:vocab_size]: # preserves the order of words in the model
            neighbours = model.most_similar(positive=[word],topn=n)
            for neighbour, sim in neighbours:
                output.write("%s\t%s\t%.4f\n" % (word, neighbour, sim))
            pb.update(i)
            i+=1
        pb.finish()   
        print("Number of processed words: %i" % i)      

def main():
    parser = argparse.ArgumentParser(description='Collect nearest words for every item in the word vector model')
    parser.add_argument("model", help="path to a word vector model")
    parser.add_argument("output", help="path to a text file for neighbours. Format: word1<TAB>neighbour1<TAB>similarity")
    parser.add_argument("-n", help="number of nearest neighbours to be collected for each word. Default 200.", default=200, type=int)
    parser.add_argument("-vocab_limit", help="collect neighbours only for specified number of most frequent words. By default use all words.", default=None, type=int)
    parser.add_argument("-format", help="model type:'word2vec' or 'gensim'. Default 'word2vec'.", default="word2vec")
    parser.add_argument("-binary", help="1 for binary model, 0 for text model. Applies to word2vec only. Default 1", default=1, type=int)
    args = parser.parse_args()
    run(args.model, args.output, args.n, args.vocab_limit, args.format, args.binary)

if __name__ == '__main__':
    main()