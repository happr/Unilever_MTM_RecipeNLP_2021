
import json
import pandas as pd
import re
from nltk.tokenize import word_tokenize
import nltk
from nltk import RegexpParser
from nltk import Tree
from nltk.stem.wordnet import WordNetLemmatizer
import numpy as np
wnl = WordNetLemmatizer()


def preprocess1(sent):
    sent = nltk.word_tokenize(sent)
    sent = nltk.pos_tag(sent)
    return sent

def process(input_json_data):

    data = json.loads(input_json_data)
    df = None
    des,quantity,unit = [],[],[]
    
    unknow_words = ['chopped',"slices","pinch","large","medium","small","each","cooked","uncooked","cooled","pot", "pouch", "packed" ,"package", "regular", "roughly" ,"slice", "sliced", "strips"]
    units = [' ml ', ' cup ',' can ',' cans ',' litres ',' litre ', ' cups '," liter "," liters ", " cm "," in ",' g ', ' oz ',' lb ', ' kg ',' kgs ', ' cm ', ' tbsp ', " ounces "," lbs ",' tsp ', ' l '," ea "]
    units_remove = ['%','/','.','-','_',']','*','-/', 'c.', 'à', 'thé','hot','pkg','plus','tbsp/','litres','litre','half','and','cubed','cube', '/-inch', "in","cm",',packages', 'pitted', 'plain' ,'thin' ,'-inch' ,'inch' ,'cube', 'cubes','thinly','tiny','finely','[','ml', 'cup',"cups",'can','cans', "liter","-in","liters", 'g', 'oz', 'kg', 'cm','lb','-lb' ,'tbsp', 'kgs','tsp', 'l',"ea","ounces","lbs","peeled","roasted"]

    for result in data['data']:
        d= result[u'ingredients'][u'ungrouped'][u'list']
        for a in d:
            m= a['description']
            m = re.sub("\. "," ",m)
            word_tokens = word_tokenize(m) 
            m  = (" ").join(word_tokens)
            
            split_string1 = m.split(',')

            done = 0
            if "," in m:
                patterns1 = """P: {<NN><,><NN>}
                                {<VBD><,><VBD>}
                                {<JJ><,><JJ>}    
                                {<VBN><,><VBN>}"""  
                PChunker1 = RegexpParser(patterns1)
                output_pattern1 = PChunker1.parse(preprocess1(m))
                for child in output_pattern1:
                    if isinstance(child, Tree):              
                        if child.label() == 'P':

                            if (child[0][1] == "VBD") and len(split_string1)<3:
                                done=1
                                substring2 = split_string1[0] + "," +split_string1[1]
                            elif child[0][1] == "NN" or child[0][1] == "VBN" or child[0][1] == "JJ":
                                done=1
                                substring2 = split_string1[0] + "," +split_string1[1]
            if done == 0:
                substring2 = split_string1[0]         
            substring2 = re.sub("and/or","or",substring2)
            substring2 = re.sub("or/and","or",substring2)
            split_string = substring2.split(' or ')
            substring1 = ""
            
            done = 0
            patterns = """P: {<JJ><CC><JJ>}
                             {<VBD><CC><VB>}
                             {<NN><CC><JJ>}
                             {<VBD><CC><JJ>}
                             {<CD><CC><CD>}""" 
            PChunker = RegexpParser(patterns)
            if " or " in substring2:
                found_pat = PChunker.parse(preprocess1(substring2))

                for child in found_pat:
                    if isinstance(child, Tree):               
                        if child.label() == 'P':
                            if child[1][0] == "or":
                                done=1
                                
                                substring1 = split_string[1]

            if done ==0:
                substring1 = split_string[0]

            substring1 = substring1.lower()
            index = 0
            u = "x"
            for x in units:
                finding = max(substring1.find(x),0)
                if finding > index:
                  index =finding
                  u = x
                    
            if u == "x" and a['unit'] != None:
                u = a['unit']
            

            s = substring1
            pattern1 = r"(\d+){}".format(u)
            pattern2 = r"(\d+/\d+){}".format(u)
            pattern3 = r"(\d+.\d+){}".format(u)

            if len(re.findall(pattern2, s))>0:
                quantity_product = re.findall(pattern2, s)[0]

            elif len(re.findall(pattern1, s))>0:
                if len(re.findall(pattern3, s))>0:
                    quantity_product = re.findall(pattern3, s)[0]

                else:
                    quantity_product = re.findall(pattern1, s)[0]
            else:
                quantity_product = a['quantity']
                
            if index !=0:
                index = index + len(u.strip())+1
            



            substring3 = substring1
            substring3 = re.sub("\(.*?\)","",substring3)
            
            
            index = [i for i in range(len(substring3)) if substring3.startswith("(", i)]

            if len(index) == 0:
                pass
            else:
                index = index[0]
                substring3 = substring3[:index]  


            index = [i for i in range(len(substring3)) if substring3.startswith(")", i)]

            if len(index) == 0:
                pass
            else:
                index = index[-1]
                substring3 = substring3[index+1:]      
            x = re.findall("\d", substring3)

            for aaa in set(x):
                substring3 = re.sub(aaa,"",substring3)
            substring4 = substring3
            word_tokens = word_tokenize(substring4) 
            filtered_sentence = [wnl.lemmatize(w) for w in word_tokens if not w in unknow_words+units_remove] 
            substring4  = (" ").join(filtered_sentence)


            substring4 = substring4.strip(",")
            substring4 = substring4.strip()
             
            u = u.strip()
            
            try:
                quantity_product =float(quantity_product)
                if u == 'litres' or u == 'litre' or u == "liter" or u == "liters" or u == "ml" or u == "l":
                    if u == "ml":
                        quantity_product = quantity_product/1000
                    u="l"
                elif u == "kgs" or u == "kg" or u == "g":
                    if u == "g":
                        quantity_product = quantity_product/1000
                    u="kg"
            except:
                pass
   
            
            des.append(substring4)
            quantity.append(quantity_product)
            unit.append(u)
            df =pd.DataFrame(zip(des,quantity,unit),columns=["food","quantity","unit"])

    return df

def create_category_list():
  bakery = []
  with open("categories_data/Bakery.txt") as f:
    bakery = [wnl.lemmatize(re.sub("\n","",a).strip().lower()) for a in f.readlines()]

  chilled = []
  with open("categories_data/Chilled.txt") as f:
    chilled = [wnl.lemmatize(re.sub("\n","",a).strip().lower()) for a in f.readlines()]

  beverages = []
  with open("categories_data/Beverages.txt") as f:
    beverages = [wnl.lemmatize(re.sub("\n","",a).strip().lower()) for a in f.readlines()]

  dairy = []
  with open("categories_data/Dairy_Eggs.txt") as f:
    dairy = [wnl.lemmatize(re.sub("\n","",a).strip().lower()) for a in f.readlines()]

  fruit = []
  with open("categories_data/Fruit_Vegetables.txt") as f:
    fruit = [wnl.lemmatize(re.sub("\n","",a).strip().lower()) for a in f.readlines()]

  grains = []
  with open("categories_data/Grains_Beans.txt") as f:
    grains = [wnl.lemmatize(re.sub("\n","",a).strip().lower()) for a in f.readlines()]

  herbs = []
  with open("categories_data/Herbs_Spices.txt") as f:
    herbs = [wnl.lemmatize(re.sub("\n","",a).strip().lower()) for a in f.readlines()]

  meat = []
  with open("categories_data/Meat_Fish _Alternatives.txt") as f:
    meat = [wnl.lemmatize(re.sub("\n","",a).strip().lower()) for a in f.readlines()]
    
  nuts = []
  with open("categories_data/Nuts_Seeds.txt") as f:
    nuts =[wnl.lemmatize(re.sub("\n","",a).strip().lower()) for a in f.readlines()]
    
  pantry = []
  with open("categories_data/Pantry.txt") as f:
    pantry = [wnl.lemmatize(re.sub("\n","",a).strip().lower()) for a in f.readlines()]

  return bakery,chilled,beverages, dairy, fruit,grains,herbs,meat,nuts,pantry


def name_cat(name,bakery,chilled,beverages, dairy, fruit,grains,herbs,meat,nuts,pantry):
  for a in bakery:
    if a in name and len(a)>0:
      return 0

  for a in chilled:
    if a in name and len(a)>0:
      return 1

  for a in beverages:
    if a in name and len(a)>0:
      return 2

  for a in dairy:
    if a in name and len(a)>0:
      return 3

  for a in fruit:
    if a in name and len(a)>0:
      return 4

  for a in grains:
    if a in name and len(a)>0:
      return 5

  for a in herbs:
    if a in name and len(a)>0:
      return 6

  for a in meat:
    if a in name and len(a)>0:
      return 7

  for a in nuts:
    if a in name and len(a)>0:
      return 8

  for a in pantry:
    if a in name and len(a)>0:
      return 9

  return 10

def read_units():
    with open("units_data/ml.txt") as f:
        ml =[wnl.lemmatize(re.sub("\n","",a).strip().lower()) for a in f.readlines()]
    
    gram = []
    with open("units_data/gram.txt") as f:
        gram = [wnl.lemmatize(re.sub("\n","",a).strip().lower()) for a in f.readlines()]

    return ml,gram

def convert_unit(substring4,unit,ml,gram):
    for m in ml:
        if m in substring4 and len(m)>0 and unit !="l" and unit !="ml":
            return "ml"
    for g in gram:
        if g in substring4 and len(g)>0 and unit !="kg" and unit !="g":
            return "g"
    return unit

def main_function(input_json):
    
    ml,gram = read_units()

    df = process(input_json)
    df1 = df.groupby(["food","unit"])
    bakery,chilled,beverages, dairy, fruit,grains,herbs,meat,nuts,pantry = create_category_list()
    json_bakery = []
    json_chilled = []
    json_beverages=[] 
    json_dairy =[] 
    json_fruit=[]
    json_grains =[] 
    json_herbs = []
    json_meat =[]
    json_nuts =[]
    json_pantry =[]
    json_others = []
    for name,group in df1:
        new = {}
        new["ingredient"]=name[0]
        try:
            if name[1] == "l" and group["quantity"].sum()<1:
                new["unit"]="ml"
                new["quantity"]=float(group["quantity"].sum()*1000)
            elif name[1] =="kg" and group["quantity"].sum()<1:
                new["unit"]="g"
                new["quantity"]=float(group["quantity"].sum()*1000)
            else:
                new["unit"]=name[1]

                if round(group["quantity"].sum(),2) == int(group["quantity"].sum())+0.99:
                    new["quantity"] = round(group["quantity"].sum(),0)
                else:
                    new["quantity"]=round(group["quantity"].sum(),2)
        except:
            
            new["unit"]=name[1]
            total = 0
            
            for qw in group["quantity"]:
                a = qw.split("/")
                
                a1 = int(a[0])
                a2 = int(a[1])
                total = total + a1/a2
                
            if round(total,2) == 0.33:
                quantity = "1/3"
            else:
                out = (total).as_integer_ratio()
                quantity = str(out[0])+"/"+str(out[1])
                if out[0] == out[1]:
                    quantity = out[0]
            
            new["quantity"] = quantity
        new["unit"] = convert_unit(new["ingredient"],new["unit"],ml,gram)
        cat = name_cat(name[0],bakery,chilled,beverages, dairy, fruit,grains,herbs,meat,nuts,pantry) 
        if cat == 0:
            json_bakery.append(new)
        elif cat == 1:
            json_chilled.append(new)
        elif cat == 2:
            json_beverages.append(new)
        elif cat == 3:
            json_dairy.append(new)
        elif cat == 4:
            json_fruit.append(new)
        elif cat == 5:
            json_grains.append(new)
        elif cat == 6:
            json_herbs.append(new)
        elif cat == 7:
            json_meat.append(new)
        elif cat == 8:
            json_nuts.append(new)
        elif cat == 9:
            json_pantry.append(new)
        elif cat == 10:
            json_others.append(new)



    final = {"Pantry":json_pantry,"Beverages":json_beverages,"Fruits and Vegetables":json_fruit,
             "Meat,Fish and Alternatives":json_meat,"Dairy and Eggs":json_dairy,
             "Chilled":json_chilled,"Grains and Beans":json_grains,"Herbs and Spices":json_herbs,
             "Nuts and Seeds":json_nuts,"Bakery":json_bakery,"You may also need":json_others}
    return final

    


def convert(o):
    if isinstance(o, np.int64):
        return int(o)
    raise TypeError


def lambda_handler(event, context):
    print(event)
    if('Authorization' in event['headers']):
        if(event['headers']['Authorization'] != "machineLearning2021"):
            return {
                "statusCode": 401,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "OPTIONS,POST",
                    "Access-Control-Allow-Headers": "X-Requested-With,content-type",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": "incorrect Unauthorization"
            }
    else:
        return {
            "statusCode": 401,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "OPTIONS,POST",
                "Access-Control-Allow-Headers": "X-Requested-With,content-type",
                "Access-Control-Allow-Origin": "*"
            },
            "body": "Missing Unauthorization"
        }

    if('body' not in event):
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "OPTIONS,POST",
                "Access-Control-Allow-Headers": "X-Requested-With,content-type",
                "Access-Control-Allow-Origin": "*"
            },
            "body": "Missing Body"
        }
    else:
        if not event['body']:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "OPTIONS,POST",
                    "Access-Control-Allow-Headers": "X-Requested-With,content-type",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": "Empty Body"
            }

    # f = open('all_recipes.json')
    # data = json.load(event['body'])
    dicti = main_function(event['body'])
    # print("Return successful in lambda handler")

    return {
        'statusCode': 200,
        'headers': {
            "Content-Type": "application/json",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "OPTIONS,POST",
            "Access-Control-Allow-Headers": "X-Requested-With,content-type",
            "Access-Control-Allow-Origin": "*"
        },
        'body': json.dumps(dicti, default=convert)
    }
