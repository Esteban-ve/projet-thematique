import random
from statistics import mean, pstdev
from collections import Counter

import os
import numpy as np
from random import choices
import matplotlib.pyplot as plt
import pandas as pd
from copy import deepcopy

from bdd import *
from match import match
from joueur import Joueur
from tournoi import Tournoi, J1_GAGNE, J2_GAGNE

from analytics import snapshots_to_df, rank_round, metrics, topk_accuracy

"""
data = {
        "Uniforme": creer_joueurs_uniformes(n),
        "Gaussienne": creer_joueurs_gaussiens(n),
        "Bimodale": creer_joueurs_bimodaux(n),
        "Asymétrique": creer_joueurs_asymetriques(n),
        "Anormale": creer_joueurs_anormale(n),
        "Remontada": creer_joueurs_remontada(n),
        "Gaussiens_elo_identique": creer_joueurs_gaussiens_elo(n, bool_elo_depart_identique=True),
        "Gaussiens_elo_aleatoire": creer_joueurs_gaussiens_elo(n, bool_elo_depart_identique=False),
        "Uniforme_variance": creer_joueurs_uniformes_variance(n)
    }
"""

def etude_tournoi(tournoi_selectionne, nb_execution, savefig=False, folder="plots"):
    n = 400

    data = {
        "Uniforme_variance": creer_joueurs_uniformes_variance(n)
    }

    if savefig:
        os.makedirs(folder, exist_ok=True)

    for name, joueurs_initiaux in data.items():

        noms = [j.nom for j in joueurs_initiaux]
        niveaux_base = np.array([j.niveau_E for j in joueurs_initiaux])
        elos_base = np.array([j.elo for j in joueurs_initiaux])

        rang_cumul = np.zeros(n)  # cumul des rangs
        rang_sq_cumul = np.zeros(n)  # cumul des carrés pour variance

        for _ in range(nb_execution):
            joueurs = [deepcopy(j) for j in joueurs_initiaux]

            tournoi = Tournoi(participants=joueurs, match=match("NIVEAU"))
            methode = getattr(tournoi, tournoi_selectionne)
            classement = methode()

            rang_dict = {}
            rang = len(classement) - 1
            for sous_liste in classement:
                for j in sous_liste:
                    rang_dict[j.nom] = rang
                rang -= 1

            for i, nom in enumerate(noms):
                r = rang_dict[nom]
                rang_cumul[i] += r
                rang_sq_cumul[i] += r**2

        rang_mean = rang_cumul / nb_execution
        rang_var = (rang_sq_cumul / nb_execution) - rang_mean**2
        rang_std = np.sqrt(rang_var)

        idx = np.argsort(niveaux_base)
        niveaux_trie = niveaux_base[idx]
        elos_trie = elos_base[idx]
        rang_mean_trie = rang_mean[idx]
        rang_std_trie = rang_std[idx]

        spearman_niv = np.corrcoef(np.argsort(niveaux_base), rang_mean)[0,1]
        spearman_elo = np.corrcoef(np.argsort(elos_base), rang_mean)[0,1]

        fig, axs = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle(f"{name} (N={n}, runs={nb_execution})", fontsize=15)

        c = '#' + ''.join(choices('0123456789ABCDEF', k=6))

        axs[0,0].hist(niveaux_base, bins=50, color=c, alpha=0.7, edgecolor='black')
        axs[0,0].set_title("Distribution Niveau")
        axs[0,0].grid(axis='y', alpha=0.3)

        x = range(n)
        axs[0,1].plot(x, niveaux_trie, label="Niveau réel", linewidth=2)
        axs[0,1].plot(x, elos_trie, label="Elo", linewidth=2)
        axs[0,1].fill_between(x, niveaux_trie, elos_trie, alpha=0.2)
        axs[0,1].set_title("Niveau vs Elo triés")
        axs[0,1].legend()
        axs[0,1].grid(alpha=0.3)

        axs[1,0].errorbar(elos_trie, rang_mean_trie, yerr=rang_std_trie, fmt='o', alpha=0.7)
        axs[1,0].invert_yaxis()
        axs[1,0].set_title("Elo → Rang (moy & std)")
        axs[1,0].text(0.05, 0.9, f"Spearman: {spearman_elo:.3f}", transform=axs[1,0].transAxes)

        axs[1,1].errorbar(niveaux_trie, rang_mean_trie, yerr=rang_std_trie, fmt='o', alpha=0.7)
        axs[1,1].invert_yaxis()
        axs[1,1].set_title("Niveau → Rang (moy & std)")
        axs[1,1].text(0.05, 0.9, f"Spearman: {spearman_niv:.3f}", transform=axs[1,1].transAxes)

        plt.tight_layout()

        if savefig:
            path = os.path.join(folder, f"{name}.png")
            plt.savefig(path, dpi=200)

        plt.show()



def etude_variance(tournoi_selectionne, nb_execution, savefig=False, folder="plots"):
    n = 400

    data = {
        "Uniforme_variance": creer_joueurs_uniformes_variance(n)
    }

    if savefig:
        os.makedirs(folder, exist_ok=True)

    for name, joueurs_initiaux in data.items():

        noms = [j.nom for j in joueurs_initiaux]
        niveaux_base = np.array([j.niveau_E for j in joueurs_initiaux])
        niveaux_v_base = np.array([j.niveau_V for j in joueurs_initiaux])

        rang_cumul = np.zeros(n)  # cumul des rangs
        rang_sq_cumul = np.zeros(n)  # cumul des carrés pour variance

        for _ in range(nb_execution):
            joueurs = [deepcopy(j) for j in joueurs_initiaux]

            tournoi = Tournoi(participants=joueurs, match=match("INTRINSEQUE"))
            methode = getattr(tournoi, tournoi_selectionne)
            classement = methode()

            rang_dict = {}
            rang = len(classement) - 1
            for sous_liste in classement:
                for j in sous_liste:
                    rang_dict[j.nom] = rang
                rang -= 1

            for i, nom in enumerate(noms):
                r = rang_dict[nom]
                rang_cumul[i] += r
                rang_sq_cumul[i] += r**2

        rang_mean = rang_cumul / nb_execution
        rang_var = (rang_sq_cumul / nb_execution) - rang_mean**2
        rang_std = np.sqrt(rang_var)

        # tri par niveau_E pour affichage
        idx = np.argsort(niveaux_base)
        niveaux_trie = niveaux_base[idx]
        niveaux_v_trie = niveaux_v_base[idx]
        rang_mean_trie = rang_mean[idx]
        rang_std_trie = rang_std[idx]

        spearman_niv_E = np.corrcoef(np.argsort(niveaux_base), rang_mean)[0,1]
        spearman_niv_V = np.corrcoef(np.argsort(niveaux_v_base), rang_mean)[0,1]

        fig, axs = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle(f"{name} (N={n}, runs={nb_execution})", fontsize=15)

        c = '#' + ''.join(choices('0123456789ABCDEF', k=6))

        # Histogramme niveaux
        axs[0,0].hist(niveaux_base, bins=50, color=c, alpha=0.7, edgecolor='black')
        axs[0,0].set_title("Distribution Niveau E")
        axs[0,0].grid(axis='y', alpha=0.3)

        # Niveau_E vs Niveau_V triés
        x = range(n)
        axs[0,1].plot(x, niveaux_trie, label="Niveau E", linewidth=2)
        axs[0,1].plot(x, niveaux_v_trie, label="Niveau V", linewidth=2)
        axs[0,1].fill_between(x, niveaux_trie, niveaux_v_trie, alpha=0.2)
        axs[0,1].set_title("Niveau E vs Niveau V triés")
        axs[0,1].legend()
        axs[0,1].grid(alpha=0.3)

        # --- Graphe 3 : maintenant Niveau E → Rang (barres)
        axs[1,0].errorbar(niveaux_trie, rang_mean_trie, yerr=rang_std_trie, fmt='o', alpha=0.7)
        axs[1,0].invert_yaxis()
        axs[1,0].set_title("Niveau E → Rang (moy & std)")
        axs[1,0].text(0.05, 0.9, f"Spearman: {spearman_niv_E:.3f}", transform=axs[1,0].transAxes)

        # --- Graphe 4 : maintenant Niveau V → Rang (barres)
        axs[1,1].errorbar(niveaux_v_trie, rang_mean_trie, yerr=rang_std_trie, fmt='o', alpha=0.7)
        axs[1,1].invert_yaxis()
        axs[1,1].set_title("Niveau V → Rang (moy & std)")
        axs[1,1].text(0.05, 0.9, f"Spearman: {spearman_niv_V:.3f}", transform=axs[1,1].transAxes)

        plt.tight_layout()

        if savefig:
            path = os.path.join(folder, f"{name}.png")
            plt.savefig(path, dpi=200)

        plt.show()


#etude_tournoi("elimination_direct", 100, savefig=False)

etude_variance("elimination_double", 100, savefig=False)


