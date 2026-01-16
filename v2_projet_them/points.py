import numpy as np

class AttributionPoints:
    
    @staticmethod
    def _applatir_et_attribuer(classement_structure, calcul_func):
        """
        Gère l'attribution des points que le classement soit une liste plate 
        ou une liste de paliers (ex-aequo).
        """
        points_attribues = {}
        rang_courant = 1
        
        for element in classement_structure:
            # Si c'est un joueur seul (cas liste plate), on le met dans une liste
            if not isinstance(element, list):
                groupe = [element]
            else:
                groupe = element
                
            # Tous les joueurs de ce groupe/palier prennent les points du rang actuel
            pts = calcul_func(rang_courant)
            
            for joueur in groupe:
                points_attribues[joueur] = pts
            
            # Le rang saute du nombre de joueurs dans le groupe
            # Ex: Si 2 joueurs sont 5ème, le prochain rang est 7 (5 + 2)
            rang_courant += len(groupe)
            
        return points_attribues

    @staticmethod
    def lineaire(classement, max_points=None):
        """
        Points = Rang
        (1er -> 1pt, 2ème -> 2pts...)
        """
        return AttributionPoints._applatir_et_attribuer(classement, lambda r: float(r))

    @staticmethod
    def exponentielle(classement, max_points=None):
        """
        Points = exp(Rang)
        (Pénalise très fortement les derniers rangs)
        """
        return AttributionPoints._applatir_et_attribuer(classement, lambda r: np.exp(r))

    @staticmethod
    def logarithmique(classement, max_points=None):
        """
        Points = log(Rang)
        (Écrase les écarts, différences faibles entre 1er et 10ème)
        Note: On évite log(0) car les rangs commencent à 1.
        """
        return AttributionPoints._applatir_et_attribuer(classement, lambda r: np.log(r) if r > 0 else 0)