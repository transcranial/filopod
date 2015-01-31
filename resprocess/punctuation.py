#takes a search term and evaluates whether it is in a certain text, with punctuation

def punctuator(term,text):
        if " " + term + " " in text: return True
        return False

def punct_count(term,text):
        c=text.count(" "+term+" ")
        return c
