import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

class MetricsAnalyzer:
    def __init__(self, joueurs):
        self.joueurs = joueurs
        # Vérité Terrain : Le meilleur a le plus haut niveau (Tri décroissant)
        self.joueurs_tries_par_niveau = sorted(joueurs, key=lambda j: j.niveau, reverse=True)

    def _get_ranking_by_system(self, system_name):
        """
        Retourne la liste des joueurs classés selon le système choisi.
        """
        if system_name == "elo":
            return sorted(self.joueurs, key=lambda j: j.elo, reverse=True)
        else:
            # Points = RANG (donc plus c'est petit, mieux c'est)
            return sorted(self.joueurs, key=lambda j: sum(j.historique_points[system_name]), reverse=False)

    def calculate_spearman(self, system_name):
        """
        Corrélation de Spearman entre le Niveau Intrinsèque et le Résultat Final.
        Vise -1.0 (Niveau Haut -> Rang Bas).
        """
        niveaux_reels = [j.niveau for j in self.joueurs]
        
        if system_name == "elo":
            resultats = [j.elo for j in self.joueurs]
        else:
            resultats = [sum(j.historique_points[system_name]) for j in self.joueurs]
            
        corr, _ = stats.spearmanr(niveaux_reels, resultats)
        return corr

    def top_bottom_accuracy(self, system_name, k=3):
        ranking_sys = self._get_ranking_by_system(system_name)
        
        true_top = set(self.joueurs_tries_par_niveau[:k])
        true_bot = set(self.joueurs_tries_par_niveau[-k:])
        
        sys_top = set(ranking_sys[:k])
        sys_bot = set(ranking_sys[-k:])
        
        acc_top = len(true_top.intersection(sys_top)) / k
        acc_bot = len(true_bot.intersection(sys_bot)) / k
        
        return acc_top, acc_bot

    def volatility_analysis(self, system_name):
        """
        MODIFIÉ : Calcule la volatilité basée sur le RANG par tournoi, 
        et non sur les points bruts.
        Cela permet de comparer Log vs Exp sur une même échelle (1 à 32).
        """
        stds_individuels = []
        
        # 1. On a besoin de reconstituer le classement de CHAQUE tournoi
        # pour savoir quel rang le joueur a obtenu (car historique_points contient des points, pas des rangs)
        
        nb_tournois = len(self.joueurs[0].historique_points[system_name]) if len(self.joueurs) > 0 else 0
        if nb_tournois < 2:
            return 0.0, 0.0

        # On prépare une structure pour stocker les rangs de chaque joueur
        # rangs_par_joueur[joueur_obj] = [rang_t1, rang_t2...]
        rangs_par_joueur = {j: [] for j in self.joueurs}

        for t_idx in range(nb_tournois):
            # Pour ce tournoi spécifique 't_idx', on récupère les points de tout le monde
            scores_tournoi = []
            for j in self.joueurs:
                pts = j.historique_points[system_name][t_idx]
                scores_tournoi.append((j, pts))
            
            # On trie pour trouver le rang (Points petits = 1er)
            if system_name == "elo":
                 # Attention: Elo change à chaque match, ici on simplifie en prenant l'elo final 
                 # ou on ignore la volatilité Elo basée sur rang tournoi par tournoi car complexe à reconstruire
                 # On renvoie 0 pour Elo ici ou on garde l'écart type des points Elo bruts
                 return 0.0, 0.0 
            else:
                # Tri croissant des points (car système pénalité)
                scores_tournoi.sort(key=lambda x: x[1])

            # On attribue le rang (1er, 2eme...)
            for rang_idx, (j, pts) in enumerate(scores_tournoi):
                vrai_rang = rang_idx + 1
                rangs_par_joueur[j].append(vrai_rang)

        # 2. Calcul de la volatilité sur ces rangs (1 à 32)
        for j in self.joueurs:
            historique_rangs = rangs_par_joueur[j]
            stds_individuels.append(np.std(historique_rangs))
        
        return np.mean(stds_individuels), np.std(stds_individuels)