from __future__ import absolute_import, division, print_function, unicode_literals
import argparse
import codecs
import csv
import os

"""
Load the cornell movie dialog corpus.

Available from here:
http://www.cs.cornell.edu/~cristian/Cornell_Movie-Dialogs_Corpus.html

"""

def loadLines(fileName, fields):
    """
    Args:
        fileName (str): file to load
        field (set<str>): fields to extract
    Return:
        dict<dict<str>>: the extracted fields for each line
    """
    lines = {}

    with open(fileName, 'r', encoding='iso-8859-1') as f:  # TODO: Solve Iso encoding pb !
        for line in f:
            values = line.split(" +++$+++ ")

            # Extract fields
            lineObj = {}
            for i, field in enumerate(fields):
                lineObj[field] = values[i]

            lines[lineObj['lineID']] = lineObj

    return lines

def loadConversations(fileName, lines, fields):
    """
    Args:
        fileName (str): file to load
        field (set<str>): fields to extract
    Return:
        dict<dict<str>>: the extracted fields for each line
    """
    conversations = []

    with open(fileName, 'r', encoding='iso-8859-1') as f:  # TODO: Solve Iso encoding pb !
        for line in f:
            values = line.split(" +++$+++ ")

            # Extract fields
            convObj = {}
            for i, field in enumerate(fields):
                convObj[field] = values[i]

            # Convert string to list (convObj["utteranceIDs"] == "['L598485', 'L598486', ...]")
            lineIds = eval(convObj["utteranceIDs"])

            # Reassemble lines
            convObj["lines"] = []
            for lineId in lineIds:
                convObj["lines"].append(lines[lineId])

            conversations.append(convObj)

    return conversations

def extractSentencePairs(conversations):
    """
    Extract the sample lines from the conversations
    """

    qa_pairs = []
    for conversation in conversations:
        # Iterate over all the lines of the conversation

        for i in range(len(conversation["lines"]) - 1):  # We ignore the last line (no answer for it)
            inputLine = conversation["lines"][i]["text"].strip()
            targetLine = conversation["lines"][i+1]["text"].strip()

            if inputLine and targetLine:  # Filter wrong samples (if one of the list is empty)
                qa_pairs.append([inputLine, targetLine])

    return qa_pairs

def main():
    """
    Parses the Cornell Movie Dialog Corpus, and extracts conversations from it.
    """

    # Parse command line args
    parser = argparse.ArgumentParser(description='Extract conversations from Cornell movie dialog corpus')

    parser.add_argument('-i', '--input', required=True,
                        help='Path to input dir')
    parser.add_argument('-d', '--delimiter', required=True, default='\t', 
                        help='Column delimiter between output columns')
    parser.add_argument('-o', '--output', required=True, help='Path to output file')

    args = parser.parse_args()
    # Unescape the delimiter
    args.delimiter = codecs.decode(args.delimiter, "unicode_escape")

    # Convert args to dict
    vargs = vars(args)

    print("\nArguments:")
    for arg in vargs:
        print("{}={}".format(arg, getattr(args, arg)))

    lines = {}
    conversations = []

    MOVIE_LINES_FIELDS = ["lineID", "characterID", "movieID", "character", "text"]
    MOVIE_CONVERSATIONS_FIELDS = ["character1ID", "character2ID", "movieID", "utteranceIDs"]

    print("\nProcessing corpus...")
    lines = loadLines(os.path.join(args.input, "movie_lines.txt"), MOVIE_LINES_FIELDS)
    print("\nLoading conversations...")
    conversations = loadConversations(os.path.join(args.input, "movie_conversations.txt"),
                                      lines, MOVIE_CONVERSATIONS_FIELDS)

    with open(args.output, 'w', encoding='iso-8859-1') as outputfile:
        writer = csv.writer(outputfile, delimiter=args.delimiter)
        
        for pair in extractSentencePairs(conversations):
            writer.writerow(pair)

    print("\nDone. Bye!")

if __name__ == '__main__':
    main()