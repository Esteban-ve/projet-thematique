# tournoi.py
from random import random

J1_GAGNE = 1
J2_GAGNE = -1
MATCH_NUL = 0


class Tournoi:
    """
    Gère un tournoi (pour l'instant : système suisse).
    - participants : liste de Joueur
    - resultats[j.nom] : score courant
    - snapshots : historique des rondes pour l'analyse (DataFrame ensuite)
    """

    def __init__(self, participants: list, match=None):
        self.participants = participants              # liste des joueurs
        self.historique_rencontres = {}              # qui a joué contre qui
        self.n_rondes = 6                            # non utilisé pour l'instant
        self.resultats = {}                          # score par nom
        self.match = match                           # pas encore utilisé

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

    def resultat_match(self, j1, j2):
        """
        Match sans nulle : on tire un vainqueur en fonction de la proba Elo
        et on met à jour les Elo des deux joueurs.
        """
        diff = j1._niveau - j2._niveau
        expected_score = 1 / (1 + 10 ** (-diff / 400))   # proba que j1 gagne
        u = random()

        if expected_score > u:
            # Victoire j1
            j1.elo += j1.K * (1 - expected_score)
            j2.elo -= j2.K * (1 - expected_score)
            return J1_GAGNE
        else:
            # Victoire j2
            j1.elo -= j1.K * expected_score
            j2.elo += j2.K * expected_score
            return J2_GAGNE

    def match_avec_egalite(self, j1, j2):
        """
        Match avec possibilité de nulle.
        On utilise le même expected_score, et on introduit une zone centrale de nulles.
        """
        diff = j1._niveau - j2._niveau
        p = 1 / (1 + 10 ** (-diff / 400))   # proba théorique que j1 gagne
        u = random()

        # Cas nulle
        if abs(p - u) < 0.01:
            s1 = 0.5
            s2 = 0.5
            j1.elo += j1.K * (s1 - p)
            j2.elo += j2.K * (s2 - (1 - p))
            return MATCH_NUL

        # Victoire j1
        elif p > u:
            s1 = 1.0
            s2 = 0.0
            j1.elo += j1.K * (s1 - p)
            j2.elo += j2.K * (s2 - (1 - p))
            return J1_GAGNE

        # Victoire j2
        else:
            s1 = 0.0
            s2 = 1.0
            j1.elo += j1.K * (s1 - p)
            j2.elo += j2.K * (s2 - (1 - p))
            return J2_GAGNE

    # ---------- appariements suisses ----------

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

    def jouer_ronde(self, n_ronde: int, avec_nulles: bool = True):
        appariements = self.créer_apparaiement_ronde_suisse()

        for j1, j2 in appariements:
            if j2 is None:
                # Gestion de l'exempt : +1 point par défaut
                self.resultats[j1.nom] += 1
                continue

            if avec_nulles:
                resultat = self.match_avec_egalite(j1, j2)
            else:
                resultat = self.resultat_match(j1, j2)

            if resultat == J1_GAGNE:
                self.resultats[j1.nom] += 1
            elif resultat == J2_GAGNE:
                self.resultats[j2.nom] += 1
            elif resultat == MATCH_NUL:
                self.resultats[j1.nom] += 0.5
                self.resultats[j2.nom] += 0.5

        self._capture_snapshot(n_ronde)

    # ---------- élimination direct ----------

def elimination_direct(self,avec_elo=False, avec_nulles: bool = True): #Si on choisi avec elo, alors le favori jouera avec le pire joueur etc
    classement_de_sorti=[]
    if avec_elo:
        joueur_actuels=sorted(
            self.participants,
            key=lambda j: (j.elo)
        )
    else:
        joueur_actuels=
    while len(joueur_actuels)>1:
        n=len(joueur_actuels)
        joueur_suivant=[]
        joueur_isole=-1
        if len(joueur_actuels)%2==1:
            if avec_elo:
                joueur_isole=0
            else:
                joueur_isole=random.randint(0,len(joueur_actuels))
            joueur_actuels=joueur_actuels[0:joueur_isole] + joueur_actuels[joueur_isole:]
            n=n-1
        
        for i in range(n/2):
            if J1_GAGNE==self.resultat_match(joueur_actuels[i],joueur_actuels[n-i]):
                joueur_suivant.append(joueur_actuels[i])
            else:
                joueur_suivant.append(joueur_actuels[n-i])

