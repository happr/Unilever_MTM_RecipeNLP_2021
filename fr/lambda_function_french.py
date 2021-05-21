import json
import pandas as pd
import re
from nltk.tokenize import word_tokenize
import nltk
import fr_core_news_sm as model
nlp = model.load()



def process(input_json_data):

    data = input_json_data
    df = None
    des,quantity,unit = [],[],[]
    
    unknow_words = ["cuillères","cuillère","à","thé","cuillère à thé","en","dés","hachée","hachées","grossièrement","divisées","finement","facultatif","haché","tassées","boîte","de","soupe","conserve","bouillon","gousses","gousse","grosse","gross","gros","lanières","livre","onces","paquet","petit","petite","récipients","sachet","tasse","tasses","râpé","non cuit","cuit","cuits","tranche","tranches","moyenne","durs","pincer","refroidi","refroidie","grande","pot","emballée","poche","paquet","ordinaire","bandes","chaude","chaudes","plus","coupées","lanières","moitié","cuillères à thé","en","cubes","cube","dénoyauté","dénoyautés","mince","minces","tout petit","pelée","pelées","rôti","rôtis",]
    units = [" onces "," ml ", " l "," g "," kg "," kgs "," oz "," cm "," tasse de "]
    units_remove = ['%','/','.','-','_','-',']','*','-/', 'c.',"[,","]","onces","ml", "l","g","kg","kgs","oz","cm"]

    for result in data['data']:
        d= result[u'ingredients'][u'non classés'][u'list']
        for a in d:
            m= a['description']
            m =re.sub("d'","de ",m)
            word_tokens = word_tokenize(m) 
            m  = (" ").join(word_tokens)
            m = re.sub("\. "," ",m)
            split_string1 = m.split(',')
            if ", " in m:
                if split_string1[1].strip() == "sans peau":
                    substring2 = split_string1[0] +", "+split_string1[1]
                else:
                    substring2 = split_string1[0]         
            else:
                substring2 = m 
                
            split_string = substring2.split(' ou ')
            substring1 = ""
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
            
            
            
            
            filtered_sentence = [nlp(w)[0].lemma_ for w in word_tokens if not w.strip() in unknow_words+units_remove] 
            substring4  = (" ").join(filtered_sentence)


            substring4 = substring4.strip(",")
            substring4 = substring4.strip()
            substring4 = re.sub("-","",substring4)

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
  with open("categories_data/Boulangerie.txt") as f:
    bakery = [re.sub("\n","",a).strip() for a in f.readlines()]

  chilled = []
  with open("categories_data/Chilled_2.txt") as f:
    chilled = [re.sub("\n","",a).strip() for a in f.readlines()]

  beverages = []
  with open("categories_data/Breuvages.txt") as f:
    beverages = [re.sub("\n","",a).strip() for a in f.readlines()]

  dairy = []
  with open("categories_data/produits_laitiers_et_œufs.txt") as f:
    dairy = [re.sub("\n","",a).strip() for a in f.readlines()]

  fruit = []
  with open("categories_data/fruits_et_légumes.txt") as f:
    fruit = [re.sub("\n","",a).strip() for a in f.readlines()]

  grains = []
  with open("categories_data/céréales_et_haricots.txt") as f:
    grains = [re.sub("\n","",a).strip() for a in f.readlines()]

  herbs = []
  with open("categories_data/herbes_et_épices.txt") as f:
    herbs = [re.sub("\n","",a).strip() for a in f.readlines()]

  meat = []
  with open("categories_data/viande_poisson_et_substituts.txt") as f:
    meat = [re.sub("\n","",a).strip() for a in f.readlines()]
    
  nuts = []
  with open("categories_data/noix_et_graines.txt") as f:
    nuts = [re.sub("\n","",a).strip() for a in f.readlines()]
    
  pantry = []
  with open("categories_data/garde-manger.txt") as f:
    pantry = [re.sub("\n","",a).strip() for a in f.readlines()]

  return bakery,chilled,beverages, dairy, fruit,grains,herbs,meat,nuts,pantry

def name_cat(name,bakery,chilled,beverages, dairy, fruit,grains,herbs,meat,nuts,pantry):
  
  for a in bakery:
    if a in name and len(a)>0:
      return 0

  for a in chilled:
    if a.lower() in name.lower() and len(a)>0:
      return 1

  for a in beverages:
    if a.lower() in name.lower() and len(a)>0:
      return 2

  for a in dairy:
    if a.lower() in name.lower() and len(a)>0:
      return 3

  for a in fruit:
    if a.lower() in name.lower() and len(a)>0:
      return 4

  for a in grains:
    if a.lower() in name.lower() and len(a)>0:
      return 5

  for a in herbs:
    if a.lower() in name.lower() and len(a)>0:
      return 6

  for a in meat:
    if a.lower() in name.lower() and len(a)>0:
      return 7

  for a in nuts:
    if a.lower() in name.lower() and len(a)>0:
      return 8

  for a in pantry:
    if a.lower() in name.lower() and len(a)>0:
      return 9

  return 10

def main_function(input_json):
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


    final = {"garde manger":json_pantry,"Breuvages":json_beverages,"fruits et légumes":json_fruit,
            "viande poisson et substituts":json_meat,"produits laitiers et œufs":json_dairy,
             "Chilled":json_chilled,"céréales et haricots":json_grains,"herbes et épices":json_herbs,
            "noix et graines":json_nuts,"Boulangerie":json_bakery,"Vous pourriez également avoir besoin":json_others}
    
    
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