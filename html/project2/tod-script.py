setOne = [1,2,3,4,5]
setTwo = [2,3,4,5,6,7,8,9,10]
def foo ():
    result = []
    for i in range(0,5):
        result.append(setOne[i] + setTwo[i])
    return result

bar = []
i = 0;
for x in setOne if len(setOne) < len(setTwo) else setTwo:
    bar.append(x + setTwo[i] if len(setOne) < len(setTwo) else setOne[i])
    i += 1

print (bar)
