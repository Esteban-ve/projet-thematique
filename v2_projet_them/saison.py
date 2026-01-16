# saison.py
from tournoi import Tournoi
from points import AttributionPoints

class Saison:
    def __init__(self, joueurs):
        self.joueurs = joueurs

    def jouer_tournoi(self, type_tournoi="suisse"):
        """
        1. Joue le tournoi selon le format demandé.
        2. Calcule les points selon TOUTES les distributions (Lin, Exp, Log).
        3. Enregistre les gains dans l'historique des joueurs.
        """
        # --- A. Exécution du Tournoi ---
        t = Tournoi(self.joueurs)
        classement = []
        
        if type_tournoi == "suisse":
            classement = t.systeme_suisse()
        elif type_tournoi == "elimination": 
            classement = t.double_elimination()
        elif type_tournoi == "round_robin":
            classement = t.round_robin()
        else:
            raise ValueError(f"Type inconnu: {type_tournoi}")

        # --- B. Attribution des points (Multi-systèmes) ---
        
        # 1. Calcul des points pour ce tournoi spécifique
        pts_lin = AttributionPoints.lineaire(classement)
        pts_exp = AttributionPoints.exponentielle(classement)
        pts_log = AttributionPoints.logarithmique(classement)

        # 2. Mise à jour des joueurs
        for joueur in self.joueurs:
            # On ajoute les points gagnés dans l'historique
            joueur.historique_points["lineaire"].append(pts_lin.get(joueur, 0))
            joueur.historique_points["exponentielle"].append(pts_exp.get(joueur, 0))
            joueur.historique_points["logarithmique"].append(pts_log.get(joueur, 0))
            
            # Pour l'Elo, on stocke la valeur courante (ou le gain, ici valeur courante)
            joueur.historique_points["elo"].append(joueur.elo)