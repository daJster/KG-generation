import re
from dateutil import parser
def clear_str(word):
    # remove all caractere like : ',|- and replace them by space
    word = re.sub(r'[\',\|\-]', ' ', word)
    return word


def text_compare(text1, text2):
    # compare two text and return a score between 0 and 1
    # 0 means that the two text are different
    # 1 means that the two text are the same
    # consider capital letters or not as the same
    # consider the order of words or not as the same
    
    # remove all caractere like : ',|- and replace them by space
    
    if text1 == text2 :
        return 1
    
    text1 = clear_str(text1)
    text2 = clear_str(text2)
    
    if text1 == text2 :
        return 1
    
    # split text into words
    words1 = text1.split()
    words2 = text2.split()
    
    # get the number of words in each text
    nb_words1 = len(words1)
    nb_words2 = len(words2)

    nb_cara1 = 0
    nb_cara2 = 0
    for word1 in words1 :
        nb_cara1 += len(word1)
    for word2 in words2 :
        nb_cara2 += len(word2)
    
    first_letters1 = ""
    first_letters2 = ""
    
    for word1 in words1 :
        if word1 != "of" and word1 != "the" and word1 != "and" :
            first_letters1 += word1[0]
    for word2 in words2 :
        if word2 != "of" and word2 != "the" and word2 != "and" :
            first_letters2 += word2[0]

    if first_letters1 == text2 :
        print("text2", text2, "is the acronym of text1", text1)
        return 1
    if first_letters2 == text1 :
        print("text1", text1, "is the acronym of text2", text2)
        return 1
    
    # if it's just the plural of the other text
    if nb_cara1 >= nb_cara2 + 1 and nb_cara1 <= nb_cara2 + nb_words2 + 1 :
        if text2 in text1 and (text1[-1] == "s" or text1[-1] == "x") and (text2[-1] != "s" and text2[-1] != "x") :
            print("text1", text1, "is the plural of text2", text2)
            return 1
    elif nb_cara2 >= nb_cara1 + 1 and nb_cara2 <= nb_cara1 + nb_words1 + 1:
        if text1 in text2 and (text2[-1] == "s" or text2[-1] == "x") and (text1[-1] != "s" and text1[-1] != "x") :
            print("text2", text2, "is the plural of text1", text1)
            return 1
    
    # get the number of words in common between the two text consider capital letters or not as the same
    nb_letters_in_common = 0
    for word1 in words1 :
        for word2 in words2 :
            for i in range(min(len(word1), len(word2))) :
                # consider é and e and è as the same
                if word1[i].lower() == word2[i].lower() or (word1[i] in "éèe" and word2[i] in "éèe"):
                    nb_letters_in_common += 1
            
    score = nb_letters_in_common / (max(len(text1), len(text2)))
    if score > 0.8 :
        print("score = ", score, "text1 = ", text1, "text2 = ", text2)
    return score


# test text_compare
print(text_compare("Business Intelligence", "BI"))
print(text_compare("Business Intelligence", "business intelligence"))
print(text_compare("Business Intelligences", "business intelligence"))
print(text_compare("Buin ligence", "business intelligences"))
print(text_compare("félicien", "felicie"))
print(text_compare("Variable dependante","variable dependante"))
print(text_compare("Renault Algeries","Algerie"))
print(text_compare("batteries", "batterie"))
print(text_compare("BSE", "Business School of Entrepreneurship"))


def detecter_date(texte):
    # Essayez de parser la date avec dateutil.parser
    try:
        try :
            # tester si texte peut être converti en int (si c'est une année)
            int(texte)
            # si oui alors regarder si c'est une année entre 1800 et 2100 si oui alors c'est une date sinon c'est pas une date
            if int(texte) >= 1800 and int(texte) <= 2100 :
                return texte
            else :
                return None
        except :
            # si ce n'est pas une année alors essayer de parser la date
            None
        date_detectee = parser.parse(texte, fuzzy=True)
        return date_detectee.strftime("%Y-%m-%d")
    except ValueError:
        return None
    return None


print("date : ", detecter_date("12/12/2020"), "12/12/2020")
print("date : ", detecter_date("12/12/20"), "12/12/20")
print("date : ", detecter_date("12/12/2020 12:12"), "12/12/2020 12:12")
print("date : ", detecter_date("Le 5 décembre 2021"), "Le 5 décembre 2021")
print("date : ", detecter_date("Le 5 déc 21"), "Le 5 déc 21")
print("date : ", detecter_date("décembre 2021"), "décembre 2021")
print("date : ", detecter_date("5 décembre"), "5 décembre")
print("date : ", detecter_date("5 déc"), "5 déc")
print("date : ", detecter_date("janvier 2021"), "janvier 2021")
print("date : ", detecter_date("janvier"), "janvier")
print("date : ", detecter_date("2021"), "2021")
print("date : ", detecter_date("2021 2022"), "2021 2022")
print("date : ", detecter_date("january 2021"), "january 2021")
print("date : ", detecter_date("133"), "133")
print("date : ", detecter_date("abc"), "abc")
print("date : ", detecter_date("1abc2"), "1abc2")
print("date : ", detecter_date("abc2122"), "abc2122")

def clear_num(text):
    #replace alpha-num-alpha by alpha-alpha and keep alpha-space-num-space-alpha
    # if there is space between the number it's ok we keep it otherwise if number is directly after or before a letter we remove the number
    
    new_text = ""
    for i in range(len(text)) :
        if text[i].isalpha() :
            new_text += text[i]
        elif text[i].isdigit() :
            if i > 0 and text[i-1].isalpha() :
                if i < len(text)-1 and text[i+1].isalpha() :
                    new_text += text[i]
            elif i < len(text)-1 and text[i+1].isalpha() :
                new_text += text[i]
            else :
                new_text += " "
        else :
            new_text += text[i]
    return new_text


        


def clear_str(word):
    # remove all caractere like : ',|- and replace them by space
    word = re.sub(r'[\',\|\-]', ' ', word)

    # if their are repetition of a word like : "the the" we remove the second "the" until there is no more repetition
    while re.search(r'(\w+) \1', word) :
        word = re.sub(r'(\w+) \1', r'\1', word)
        
    # if a word is ending with numbers without space like : "the2" we remove the numbers
    
                
    word = clear_num(word)
    # delete double space
    word = re.sub(r' +', ' ', word)
    
    return word

print(clear_str("the the"))
print(clear_str("1the2"))
print(clear_str("the2122"))
print(clear_str("Ceci 1est 34 3un1 test2")) 
print(clear_str("223 234"))
