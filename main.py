# coucou c'est le main

### les biblio

from random import uniform


### Les paramètres

nb_de_joueurs=100

list_joueurs=[]



### les fonctions

def combat(a,b):
    diff=a-b    # Attention est-ce qu'on nivelle la diff entre les niveaux des joueurs à 400 max (pour l'instant on ne le fait pas)
    p=1/(1 + 10**(-diff/400))
    
    return p > uniform(0,1)


n=1000
k=0
for i in range(n):
    if combat(801,300):
        k+=1
print(k/n*100)




