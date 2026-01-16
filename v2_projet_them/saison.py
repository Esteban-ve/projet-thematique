# saison.py
from tournoi import Tournoi
from points import AttributionPoints

class Saison:
    def __init__(self, joueurs):
        self.joueurs = joueurs

    def jouer_tournoi(self, type_tournoi="suisse"):
        t = Tournoi(self.joueurs)

        # --- Exécution du tournoi ---
        if type_tournoi == "suisse":
            liste = t.systeme_suisse()
            classement = t.classement_avec_rangs(liste, t.scores)

        elif type_tournoi == "elimination":
            liste = t.double_elimination()
            # double elimination ne génère pas de scores → on fabrique un pseudo-score
            scores = {j: len(liste)-i for i,j in enumerate(liste)}
            classement = t.classement_avec_rangs(liste, scores)

        elif type_tournoi == "round_robin":
            liste, local_scores = t.round_robin(return_scores=True)
            classement = t.classement_avec_rangs(liste, local_scores)

        else:
            raise ValueError(f"Type inconnu: {type_tournoi}")

        # --- Attribution des points ---
        pts_lin = AttributionPoints.lineaire(classement)
        pts_exp = AttributionPoints.exponentielle(classement)
        pts_log = AttributionPoints.logarithmique(classement)

        # --- Mise à jour des historiques ---
        for joueur in self.joueurs:
            joueur.historique_points["lineaire"].append(pts_lin.get(joueur, 0))
            joueur.historique_points["exponentielle"].append(pts_exp.get(joueur, 0))
            joueur.historique_points["logarithmique"].append(pts_log.get(joueur, 0))
            joueur.historique_points["elo"].append(joueur.elo)
