import re
from numpy import random as rn
from time import time


def regex_search(names, tgt):
    std = re.compile(r"\d*" + tgt + r"\d*")

    result = [item for item in names if re.fullmatch(std, item) is not None]
    return result
    
def normal_search(names, tgt):

    result = []
    for name in names:
        temp = ''
        for cont in range(0, len(name)):
            if not name[cont].isdecimal():
                temp += name[cont]
        if temp == tgt:
            result.append(name)
    
    return result


listrange = 10000000

ss = []

for cont in range(0, listrange):
    num1 = rn.randint(0,100)
    
    s = ''
    nums = rn.randint(97,123,6)
    
    for num in nums:
        s += int(num).to_bytes().decode()
    
    num2 = rn.randint(0, 100)
    
    s = str(num1) + s + str(num2)
    ss.append(s)


for cont in range(0, 15):
    ss[rn.randint(0, listrange)] = str(rn.randint(0, 100)) + 'casavt' + str(rn.randint(0, 100))
    
print(f"\nString para busca:\n{ss}")

t0 = time()        
res = regex_search(ss, 'casavt')
elapsed = time() - t0
print(f"\nBusca por regex durou {elapsed} segundos. Resultado:\n{res}")


t0 = time()
res = normal_search(ss, 'casavt')
elapsed = time() - t0
print(f"\nBusca normal durou {elapsed} segundos. Resultado:\n{res}")