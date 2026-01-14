# methodes qui prennent en entrée un classement de joueurs et leur attribue des points
# elles renvoient un dictionnaire associant chaque joueur à son nombre de points
# on considère qu'un classement est une liste de joueurs, du meilleur au pire
# attribution en ELO : pas d'étape de classement donc à coder direct dans le tournoi

from numpy import log

def attribution_linéaire(classement, alpha=1):   # dernier : +alpha point   permier : +alpha*n_joueurs points
    n_joueurs = len(classement)
    points = {}
    i=0
    while i<n_joueurs:
        points[classement[i]]=alpha*(n_joueurs-i)
        i+=1
    return points

def attribution_puissance(classement, alpha=2):    # dernier : +1 point    premier : +alpha**(n_joueurs-1) points
    n_joueurs = len(classement)            
    points = {}
    i=0
    while i<n_joueurs:
        points[classement[i]]=pow(alpha,n_joueurs-i-1)
        i+=1
    return points


def attribution_log(classement, alpha):     # attribue les points selon la fonction inverse de alpha^x, càd ln(x)/ln(alpha)
    n_joueurs = len(classement)             # dernier : +0points     premier : +log(n_joueurs)/log(alpha)
    points = {}
    i=0
    while i<n_joueurs:
        points[classement[i]]=log(n_joueurs-i)/log(alpha)
        i+=1
    return points