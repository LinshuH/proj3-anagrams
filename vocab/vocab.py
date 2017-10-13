"""
A list of vocabulary words (designed for an ELL class).
"""


class Vocab():
    """
    A list of vocabularly words.
    Can be instantiated with a file or list of strings.
    """
    # Vocab determine whether the input text is on the word list. (words)
    def __init__(self, wordlist):
        """
        Initialize with the provided word list.
        Args:
           wordlist: a file, path to a file, or a list of strings.
           Words must appear one to a line. Empty lines and lines
           beginning with # are treated as comments.
        Returns: nothing
        Effect: the new Vocab objects contains the strings from wordlist
        Raises:  IOError if if wordlist is a bad path
        """
        self.words = []
        if isinstance(wordlist, str):
            ls = open(wordlist, 'r')
        else:
            ls = wordlist

        for word in ls:
            word = word.strip()
            if len(word) == 0 or word.startswith("#"):
                continue
            self.words.append(word)  
        self.words.sort()
        # "words" contain all the word in wordlist.
        #They are formate as a new line for each new one, and they are sorted

    def as_list(self):
        """As list of words"""
        return self.words    # get the words

    def has(self, word):
        """
        Is word present in vocabulary list?
        Args:
           word: a string
        Reurns: true if word occurs in the vocabularly list
        """
        low = 0
        high = len(self.words) - 1  # so high is index?
        while low <= high:
            mid = (low + high) // 2
            probe = self.words[mid]
            if word > probe:    
                low = mid + 1
            elif word < probe:
                high = mid - 1
            else:
                return True
            # The logic here is based on the value of each letter. If the value of words are
            # same, this means they have the same character, but, how do we know the sequence
            # of the letter? How do we know "sa" is false and "as" is true?
        return False
