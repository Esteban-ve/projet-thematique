# methodes qui prennent en entrée un classement de joueurs et leur attribue des points
# elles renvoient un dictionnaire associant chaque joueur à son nombre de points
# on considère qu'un classement est une liste de joueurs, du meilleur au pire
# attribution en ELO : pas d'étape de classement donc à coder direct dans le tournoi

from numpy import log

def attribution_linéaire(classement: list, alpha=1):   # dernier : +alpha point   permier : +alpha*n_rangs points
    n_joueurs = len(classement)
    n_rangs = max(list(classement.values()))
    points = {}
    for j,rang in classement.items():
        points[j]=(n_rangs-rang+1)*alpha
    return points

def attribution_puissance(classement, alpha=2):    # dernier : +1 point    premier : +alpha**(n_rangs-1) points
    n_joueurs = len(classement)   
    n_rangs = max(list(classement.values()))         
    points = {}
    i=0
    for j,rang in classement.items():
        points[j]=pow(alpha,(n_rangs-rang))
    return points


def attribution_log(classement, alpha=2):     # attribue les points selon la fonction inverse de alpha^x, càd ln(x)/ln(alpha)
    n_joueurs = len(classement)             # dernier : +0points     premier : +log(n_rangs)/log(alpha)
    n_rangs=max(list(classement.values()))
    points = {}
    i=0
    for j,rang in classement.items():
        points[j]=log(n_rangs-rang+1)/log(alpha)
    return points


# inutilisé car on aura pas le temps de fit
"""   
def attribution_poly(classement,a,b,c,d,e):    
    # attribution selon ax^5+bx^4+cx^3+dx^2+e^x avec x le classement d'un joueur
    # pour le fitting
    n_joueurs = len(classement)
    points = {}
    i = 0
    while i<n_joueurs:
        points[classement[i]]=a*i**5+b*i**4+c*i**3+d*i**2+e*i
        i+=1
    return points
"""