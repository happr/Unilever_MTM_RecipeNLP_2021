from nltk.tokenize import word_tokenize

dictionary = {"grilles":"griller"}

def singularize(word):
    all_words = word_tokenize(word)
    full = ""
    for word1 in all_words:
        for GRAMMAR_RULE in (_dictionary_return,_eau_word_sing, _ail_word_sing, _eil_word_sing, _eu_word_sing, _ou_word_sing, _s_word_sing, _default_sing):
            singular = GRAMMAR_RULE(word1)
            if singular:
                full = full +" "+singular
                break
    return full.strip()


def _dictionary_return(word):
    if word in dictionary:
        return dictionary[word]    
        
def _eau_word_sing(word):
    if word.endswith("eaux"):
        return word[:-1]

def _ail_word_sing(word):
    if word == "aulx":
        return "ail"
    if word.endswith("aux"):
        if word in ("baux", "coraux", u"émaux", "fermaux", "soupiraux", "travaux", "vantaux", "ventaux", "vitraux"):
            return word[:-3] + "ail"
        else:
            return word[:-3] + "al"

def _eil_word_sing(word):
    if word == "vieux":
        return "vieil"

def _eu_word_sing(word):
    if word.endswith("eus") or word.endswith("eux"):
        return word[:-1]

def _ou_word_sing(word):
    if word.endswith("oux"):
        if word in ("bijoux", "cailloux", "choux", "genoux", "hiboux", "joujoux", "poux"):
            return word[:-1]
        else:
            return word

def _s_word_sing(word):
    if word.endswith("s"):
        if word in (u"abcès", u"accès", "abus", "albatros", "anchois", "anglais", "autobus", "brebis", "carquois", "cas", "chas", "colis", "concours", "corps", "cours", u"cyprès", u"décès", "devis", "discours", "dos", "embarras", "engrais", "entrelacs", u"excès", "fois", "fonds", u"gâchis", "gars", "glas", "guet-apens", u"héros", "intrus", "jars", "jus", u"kermès", "lacis", "legs", "lilas", "marais", "matelas", u"mépris", "mets", "mois", "mors", "obus", "os", "palais", "paradis", "parcours", "pardessus", "pays", "plusieurs", "poids", "pois", "pouls", "printemps", "processus", u"progrès", "puits", "pus", "rabais", "radis", "recors", "recours", "refus", "relais", "remords", "remous", u"rhinocéros", "repas", "rubis", "sas", "secours", "souris", u"succès", "talus", "tapis", "taudis", "temps", "tiers", "univers", "velours", "verglas", "vernis", "virus", "accordailles", "affres", "aguets", "alentours", "ambages", "annales", "appointements", "archives", "armoiries", u"arrérages", "arrhes", "calendes", "cliques", "complies", u"condoléances", "confins", u"dépens", u"ébats", "entrailles", u"épousailles", "errements", "fiançailles", "frais", u"funérailles", "gens", "honoraires", "matines", "mœurs", u"obsèques", u"pénates", "pierreries", u"préparatifs", "relevailles", "rillettes", u"sévices", u"ténèbres", "thermes", "us", u"vêpres", "victuailles","sans","Couscous"):
            return word
        else:
            return word[:-1]

def _default_sing(word):
    return word
