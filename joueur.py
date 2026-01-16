# joueur.py
class Joueur:
    def __init__(self, nom: str, niveau: float, elo: float = 1200):
        self.nom = nom
        self.niveau = niveau  # Force intrinsèque (Vérité terrain)
        self.elo = elo        # Force perçue (évolue)
        self.elo_initial = elo
        
        # Dictionnaire pour stocker l'historique des points gagnés à chaque tournoi
        # Ex: self.historique_points['lineaire'] = [10, 15, 8, ...]
        self.historique_points = {
            "lineaire": [],
            "exponentielle": [],
            "logarithmique": [],
            "elo": [] # On stockera l'évolution de l'Elo ici
        }

    @property
    def total_points(self):
        """Renvoie la somme des points pour chaque catégorie."""
        return {k: sum(v) for k, v in self.historique_points.items()}

    def __repr__(self):
        return f"[{self.nom} | Niv:{int(self.niveau)} | Elo:{int(self.elo)}]"