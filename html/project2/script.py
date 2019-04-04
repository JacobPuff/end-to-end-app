setOne = [1,2,3,4,5]
setTwo = [2,3,4,5,6]
def foo ():
    result = []
    for i in range(0,5):
        result.append(setOne[i] + setTwo[i])
    return result    
        
bar = foo()
print (bar)
