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
        CORRECTION IMPORTANTE : 
        - Elo : Plus c'est haut, mieux c'est (reverse=True)
        - Points (Rang) : Plus c'est bas, mieux c'est (reverse=False)
        """
        if system_name == "elo":
            return sorted(self.joueurs, key=lambda j: j.elo, reverse=True)
        else:
            # On trie par ordre CROISSANT des points (le score 1 est devant le score 10)
            return sorted(self.joueurs, key=lambda j: sum(j.historique_points[system_name]), reverse=False)

    def calculate_spearman(self, system_name):
        """
        Corrélation.
        Attention : Avec Points=Rang, on vise une corrélation de -1.
        (Niveau Haut associe à Points Bas).
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
        # Attention : le "Bas" du classement est la fin de la liste, 
        # peu importe comment elle est triée, c'est toujours les derniers éléments [-k:]
        sys_bot = set(ranking_sys[-k:])
        
        acc_top = len(true_top.intersection(sys_top)) / k
        acc_bot = len(true_bot.intersection(sys_bot)) / k
        
        return acc_top, acc_bot

    def volatility_analysis(self, system_name):
        stds_individuels = []
        for j in self.joueurs:
            historique = j.historique_points[system_name]
            if len(historique) > 1:
                stds_individuels.append(np.std(historique))
            else:
                stds_individuels.append(0.0)
        
        return np.mean(stds_individuels), np.std(stds_individuels)
    


class MetricsAnalyzerRanking:
    def __init__(self, joueurs):
        self.joueurs = joueurs
        # Vérité Terrain : Le meilleur a le plus haut niveau (Tri décroissant)
        self.joueurs_tries_par_niveau = sorted(joueurs, key=lambda j: j.niveau, reverse=True)

    def _get_ranking_by_system(self, system_name):
        """
        Retourne la liste des joueurs classés selon le système choisi.
        CORRECTION IMPORTANTE : 
        - Elo : Plus c'est haut, mieux c'est (reverse=True)
        - Points (Rang) : Plus c'est bas, mieux c'est (reverse=False)
        """
        if system_name == "elo":
            return sorted(self.joueurs, key=lambda j: j.elo, reverse=True)
        else:
            # On trie par ordre CROISSANT des points (le score 1 est devant le score 10)
            return sorted(self.joueurs, key=lambda j: sum(j.historique_points[system_name]), reverse=False)

    def calculate_spearman(self, system_name):
        """
        Corrélation.
        Attention : Avec Points=Rang, on vise une corrélation de -1.
        (Niveau Haut associe à Points Bas).
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
        # Attention : le "Bas" du classement est la fin de la liste, 
        # peu importe comment elle est triée, c'est toujours les derniers éléments [-k:]
        sys_bot = set(ranking_sys[-k:])
        
        acc_top = len(true_top.intersection(sys_top)) / k
        acc_bot = len(true_bot.intersection(sys_bot)) / k
        
        return acc_top, acc_bot

    def volatility_analysis(self, system_name):
        stds_individuels = []
        for j in self.joueurs:
            historique = j.historique_points[system_name]
            if len(historique) > 1:
                stds_individuels.append(np.std(historique))
            else:
                stds_individuels.append(0.0)
        
        return np.mean(stds_individuels), np.std(stds_individuels)