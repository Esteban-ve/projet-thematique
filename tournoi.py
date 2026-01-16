# tournoi.py
from random import random, shuffle, randint
import numpy as np
from match import Match
from math import ceil

J1_GAGNE = 1
J2_GAGNE = -1


class Tournoi:
    """
    Gère un tournoi (pour l'instant : système suisse).
    - participants : liste de Joueur
    - resultats[j.nom] : score courant
    - snapshots : historique des rondes pour l'analyse (DataFrame ensuite)
    """

    def __init__(self, participants: list, match):
        assert isinstance(match, Match)
        self.participants = participants              # liste des joueurs
        self.historique_rencontres = {}              # qui a joué contre qui
        self.n_rondes = 6                            # non utilisé pour l'instant
        self.resultats = {}                          # score par nom
        self.match = match                      # pas encore utilisé

        self.snapshots = []                          # pour analytics
        
        self.init_results()
        self.init_historique_rencontres()

    # ---------- initialisation ----------

    def type(self, tournoi, avec_elo:bool=True, taille_poule:int=4, n_qualifies:int=8,n_rondes:int=6):
        type_tournoi ={
            "swiss_round": self.swiss_rounde(avec_elo,n_rondes), 
            "elimination_directe": self.elimination_directe(avec_elo),
            "round_robin": self.round_robin(avec_elo),
            "poule_elimination_directe": self.poule_elimination_directe(avec_elo,taille_poule),
            "elemination_double": self.elimination_double(avec_elo),
            "ligue_1": self.ligue_1(avec_elo),
            "ligue_playoff": self.ligue_playoff(avec_elo,n_qualifies),
            }  # type de tournoi
        return type_tournoi[tournoi]
    def init_historique_rencontres(self):
        for participant in self.participants:
            self.historique_rencontres[participant] = []

    def init_results(self):
        for participant in self.participants:
            self.resultats[participant.nom] = 0

    def _capture_snapshot(self, n_ronde: int):
        """Sauvegarde l’état du tournoi après la ronde n_ronde."""
        snap = []
        for j in self.participants:
            snap.append({
                "ronde": n_ronde,
                "nom": j.nom,
                "score": self.resultats[j.nom],
                "elo": j.elo,
                "niveau_reel": getattr(j, "_niveau", None),
            })
        self.snapshots.append(snap)

    # ---------- simulation d'un match ----------

    def créer_apparaiement_ronde_suisse(self, avec_elo: bool = True):
        """
        Crée les appariements d'une ronde suisse :
        - tri par (score, elo)
        - on essaie d'éviter les re-matches en utilisant historique_rencontres
        - dernier joueur non apparié -> exempt (None)
        """
        n_participants = len(self.participants)
        if avec_elo:
            participants_classés = sorted(
            self.participants,
            key=lambda j: (self.resultats[j.nom], j.elo),
            reverse=True,
            )  # classemeent en fonction du nombre de points et de l'elo
        else:
            participants_classés = sorted(
            self.participants,
            key=lambda j: (self.resultats[j.nom]),
            reverse=True,
            )  # classemeent en fonction du nombre de points uniquement
        
        appariements = []
        deja_paires = set()
        i = 0

        while i < n_participants:
            j1 = participants_classés[i]

            if j1 in deja_paires:
                i += 1
                continue

            candidats_restants = [
                j for j in participants_classés[i + 1:]
                if j not in deja_paires
            ]

            if not candidats_restants:
                appariements.append((j1, None))
                deja_paires.add(j1)
                break

            adversaire = None
            for candidat in candidats_restants:
                if candidat not in self.historique_rencontres[j1]:
                    adversaire = candidat
                    break
            if adversaire is None:
                adversaire = candidats_restants[0]

            appariements.append((j1, adversaire))
            deja_paires.add(j1)
            deja_paires.add(adversaire)

            i += 1

        # mise à jour historique
        for j1, j2 in appariements:
            if j2 is not None:
                self.historique_rencontres[j1].append(j2)
                self.historique_rencontres[j2].append(j1)

        return appariements

    # ---------- déroulement d'une ronde ----------

    def jouer_ronde(self, n_ronde: int,avec_elo: bool = True):
        appariements = self.créer_apparaiement_ronde_suisse(avec_elo)

        for j1, j2 in appariements:
            if j2 is None:
                # Gestion de l'exempt : +1 point par défaut
                self.resultats[j1.nom] += 1
                continue

            resultat = self.match.resultat(j1, j2)
            if resultat == J1_GAGNE:
                self.resultats[j1.nom] += 1
            elif resultat == J2_GAGNE:
                self.resultats[j2.nom] += 1
    
        self._capture_snapshot(n_ronde)

        # ---------- élimination direct ----------

    def elimination_directe(self,avec_elo=True): #Si on choisi avec elo, alors le favori jouera avec le pire joueur etc. Sinon : aléatoire
        classement_de_sortie={}     # joueur:classement
        classement_actuel = ceil(np.log2(len(self.participants))+1)   # si un joueur perd à ce round il aura ce classement
        joueurs_actuels=[]
        if avec_elo:
            joueurs_actuels=sorted(
                self.participants,
                key=lambda j: (j.elo),
                reverse=True
            ) #du meilleur au moins bon
        else:
            joueurs_actuels=self.participants.copy()
            shuffle(joueurs_actuels)

        while len(joueurs_actuels)>1:
            perdant=[]
            n=len(joueurs_actuels)
            joueurs_suivants=[]
            joueur_isole=-1
            if len(joueurs_actuels)%2==1:
                if avec_elo:
                    joueur_isole=0
                else:
                    joueur_isole=randint(0,len(joueurs_actuels)-1)
                joueurs_suivants.append(joueurs_actuels[joueur_isole])
                #del joueurs_actuels[joueur_isole]
                joueurs_actuels.pop(joueur_isole)
                n=n-1
            
            for i in range(n//2):
                if self.match.resultat(joueurs_actuels[i],joueurs_actuels[n-1-i])==J1_GAGNE:
                    joueurs_suivants.append(joueurs_actuels[i])
                    classement_de_sortie[joueurs_actuels[n-i-1]]=classement_actuel
                    perdant.append(joueurs_actuels[n-1-i])
                else:
                    joueurs_suivants.append(joueurs_actuels[n-1-i])
                    classement_de_sortie[joueurs_actuels[i]]=classement_actuel
                    perdant.append(joueurs_actuels[i])
            joueurs_actuels=joueurs_suivants
            classement_actuel-=1
        classement_de_sortie[joueurs_actuels[0]] = classement_actuel   # dernier joueur, gagnant ultime
        return classement_de_sortie
    
    def poule_elimination_directe(self, avec_elo:bool=True, taille_poule:int=4):
        classement_de_sortie=[]
        joueurs_actuels=[]

        if avec_elo:
            joueurs_actuels=sorted(
                self.participants,
                key=lambda j: (j.elo),
                reverse=True
            ) #du meilleur au moins bon
        else:
            joueurs_actuels=self.participants
            random.shuffle(joueurs_actuels)

        nombre_de_poule=len(joueurs_actuels)//taille_poule
        poules=[]

        for i in range(nombre_de_poule):
            poules.append(joueurs_actuels[i*taille_poule:(i+1)*taille_poule])
        
        for poule in poules:
            tournoi_poule=Tournoi(poule,self.match)
            tournoi_poule.elimination_direct(avec_elo)
            classement_de_sortie.append(tournoi_poule.classement_de_sortie)
        
        return classement_de_sortie
    
    def elimination_double(self,avec_elo:bool=True):
        classement_finale=[]
        joueur_haut=[]
        joueur_bas=[]
        if avec_elo:
            joueur_haut=sorted(
                self.participants,
                key=lambda j: (j.elo),
                reverse=True
            ) #du meilleur au moins bon
        else:
            joueur_haut=self.participants
            random.shuffle(joueur_haut)
        while len(joueur_haut)>1:
            n=len(joueur_haut)
            joueur_survivant=[]
            for i in range(n//2):
                
                if J1_GAGNE==self.match.resultat(joueur_haut[i],joueur_haut[n-i-1]):
                    joueur_bas.append(joueur_haut[n-i-1])
                    joueur_survivant.append(joueur_haut[i])
                else:
                    joueur_bas.append(joueur_haut[i])
                    joueur_survivant.append(joueur_haut[n-i-1])
            joueur_haut=joueur_survivant
            m= len(joueur_bas)
            joueur_survivant_bas=[]
            while len(joueur_bas)!=len(joueur_haut)/2:
                m=len(joueur_bas)
                joueur_survivant_bas=[]
                for j in range(m//2):
                    if J1_GAGNE==self.match.resultat(joueur_bas[j],joueur_bas[m-j-1]):
                        classement_finale.append(joueur_bas[m-j-1])
                        joueur_survivant_bas.append(joueur_bas[j])
                    else:
                        classement_finale.append(joueur_bas[j])
                        joueur_survivant_bas.append(joueur_bas[m-j-1])
                joueur_bas=joueur_survivant_bas
        classement_finale.append(joueur_haut[0])
        return classement_finale
    
    def ligue_1(self,avec_elo:bool=True): #TODO: attribué des niveau selon domicile ou exterieur
        classement_finale=[]
        score = { j.nom:0 for j in self.participants 
                    }
        for i in range (len(self.participants)):#Match aller
            for j in range (i+1,len(self.participants)):
                if J1_GAGNE==self.match.resultat(self.participants[i],self.participants[j]):
                    score[self.participants[i].nom]+=1
                else:
                    score[self.participants[j].nom]+=1
        
        for i in range(len(self.participants)): #Match retour
            for j in range (i+1,len(self.participants)):
                if J1_GAGNE==self.match.resultat(self.participants[i],self.participants[j]):
                    score[self.participants[i].nom]+=1
                else:
                    score[self.participants[j].nom]+=1
        classement_finale=sorted(
            self.participants,
            key=lambda j: (score[j.nom]),
            reverse=True
        )

        return classement_finale #Retourne la liste des joueurs dans l'ordre du classement du premier au dernier

    def ligue_playoff(self, avec_elo:bool=True, n_qualifies:int=8):
        classement_temporaire=self.ligue_1(avec_elo)
        qualifies=classement_temporaire[:n_qualifies]
        tournoi_playoff=Tournoi(qualifies,self.match)
        classement_finale=tournoi_playoff.elimination_direct(avec_elo)
        return classement_finale

    def swiss_round(self, n_rondes:int=6, avec_elo:bool=True):
        for n in range(n_rondes):
            self.jouer_ronde(n+1, avec_elo)
        classement_finale=sorted(
            self.participants,
            key=lambda j: (self.resultats[j.nom], j.elo),
            reverse=True
        )
        return classement_finale

    def round_robin(self, avec_elo:bool=True):
        for i in range (len(self.participants)):
            for j in range (i+1,len(self.participants)):
                if J1_GAGNE==self.match.resultat(self.participants[i],self.participants[j]):
                    self.resultats[self.participants[i].nom]+=1
                else:
                    self.resultats[self.participants[j].nom]+=1
        classement_finale=sorted(
            self.participants,
            key=lambda j: (self.resultats[j.nom], j.elo),
            reverse=True
        )
        return classement_finale