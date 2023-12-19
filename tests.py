import json

with open(r"C:\Users\GEPH-IC\Documents\Betson\Laudo Pericial\arquivos\dicPlural.json", "r", encoding='utf-8') as f:
    dic = json.loads(f.read())
    f.close()
 
print(dic)
input()