# tournoi.py
from random import random

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
        self.participants = participants              # liste des joueurs
        self.historique_rencontres = {}              # qui a joué contre qui
        self.n_rondes = 6                            # non utilisé pour l'instant
        self.resultats = {}                          # score par nom
        self.match = match                      # pas encore utilisé

        self.snapshots = []                          # pour analytics

        self.init_results()
        self.init_historique_rencontres()

    # ---------- initialisation ----------

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

    def créer_apparaiement_ronde_suisse(self):
        """
        Crée les appariements d'une ronde suisse :
        - tri par (score, elo)
        - on essaie d'éviter les re-matches en utilisant historique_rencontres
        - dernier joueur non apparié -> exempt (None)
        """
        n_participants = len(self.participants)
        participants_classés = sorted(
            self.participants,
            key=lambda j: (self.resultats[j.nom], j.elo),
            reverse=True,
        )
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

    def jouer_ronde(self, n_ronde: int):
        appariements = self.créer_apparaiement_ronde_suisse()

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

    def elimination_direct(self,avec_elo=False, avec_nulles: bool = False): #Si on choisi avec elo, alors le favori jouera avec le pire joueur etc
        classement_de_sorti=[]
        joueur_actuels=[]

        if avec_elo:
            joueur_actuels=sorted(
                self.participants,
                key=lambda j: (j.elo),
                reverse=True
            ) #du meilleur au moins bon
        else:
            joueur_actuels=self.participants
            joueur_actuels=random.shuffle(joueur_actuels)

        while len(joueur_actuels)>1:
            perdant=[]
            n=len(joueur_actuels)
            joueur_suivants=[]
            joueur_isole=-1
            if len(joueur_actuels)%2==1:
                if avec_elo:
                    joueur_isole=0
                else:
                    joueur_isole=random.randint(0,len(joueur_actuels))
                joueur_actuels=joueur_actuels[0:joueur_isole] + joueur_actuels[joueur_isole:]
                joueur_suivants.append(joueur_actuels[joueur_isole])
                n=n-1
            
            for i in range(n/2):
                if J1_GAGNE==self.match.resultat(joueur_actuels[i],joueur_actuels[n-i]):
                    joueur_suivants.append(joueur_actuels[i])
                    perdant.append(joueur_actuels[n-i])
                else:
                    joueur_suivants.append(joueur_actuels[n-i])
                    perdant.append(joueur_actuels[i])
            if avec_elo:
                joueur_actuels=sorted(
                    joueur_suivants,
                    key=lambda j: (j.elo),
                    reverse=True
                ) #du meilleur au moins bon
            else:
                joueur_actuels=joueur_suivants
            classement_de_sorti.append(perdant)
        rang_final=1
        return classement_de_sorti
    
