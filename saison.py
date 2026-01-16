from random import random
from tournoi import Tournoi
from joueur import Joueur

class Saison:
    def __init__(self, joueurs: list, tournois: list):
        self.participants = []# Liste des participants de la saison
        for j in joueurs:
            self.participants.append(self.Participant(j, taux_participation=1, richesse=0))#par défaut les joueurs participent à tous les tournois
        self.tournois = []# Liste des tournois de la saison
        for t in tournois:
            param= t.split(",")#récupère les paramètres du tournoi (Type, avecbool, taille_poule, n_qualifies, n_rondes)
            self.tournois.append(param)
    
    class Participant(Joueur): # Classe interne représentant un participant à la saison avec son taux de participation et sa richesse( capacité à payer les frais d'inscription)
        def __init__(self, nom, niveau_E=0, niveau_V=0, K=40, elo=1500, taux_participation=1, richesse=0):
            super().__init__(nom, niveau_E, niveau_V, K, elo)
            self.probabilite_participation = taux_participation
            self.richesse = richesse
            self.point = 0
            self.classement = None

        def participe(self):
            return random() < self.probabilite_participation
    
    def complete(self,participants):# tout le monde participe à tous les tournois
        for tournoi in self.tournois:
            T=Tournoi(participants)
            if len(tournoi)==1:
                classement_intermediaire=T.type(tournoi[0])
            elif len(tournoi)==2:
                classement_intermediaire=T.type(tournoi[0],exec(tournoi[1]))
            elif len(tournoi)==3:
                classement_intermediaire=T.type(tournoi[0],exec(tournoi[1]), exec(tournoi[2]))
            for j,p in enumerate(self.participants):
                p.classement=classement_intermediaire.index(p.joueur)+1
            Classement=T.type(tournoi[0],avec_elo=bool(tournoi[1]), taille_poule=int(tournoi[2]), n_qualifies=int(tournoi[3]), n_rondes=int(tournoi[4]))