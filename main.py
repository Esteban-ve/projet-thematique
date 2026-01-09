# main.py
import random
from statistics import mean, pstdev
from collections import Counter

import os
import numpy as np
from random import choices
import matplotlib.pyplot as plt
import pandas as pd

from bdd import *
from match import match
from joueur import Joueur
from tournoi import Tournoi, J1_GAGNE, J2_GAGNE

from analytics import snapshots_to_df, rank_round, metrics, topk_accuracy

# ---------- 1. SIMULATION D'UN TOURNOI SUISSE ----------

def simuler_un_tournoi(nb_rondes: int, seed: int | None = None):
    if seed is not None:
        random.seed(seed)

    joueurs = joueurs_belloy()
    tournoi = Tournoi(participants=joueurs, match=match("NIVEAU"))

    for r in range(1, nb_rondes + 1):
        tournoi.jouer_ronde(r)

    df_all = snapshots_to_df(tournoi.snapshots)
    dernier = df_all["ronde"].max()
    df_last = rank_round(df_all[df_all["ronde"] == dernier])

    m = metrics(df_last)
    top3 = topk_accuracy(df_last, k=3)

    df_sorted_rank = df_last.sort_values("rang")
    champion = df_sorted_rank.iloc[0]
    meilleur_vrai = df_last.sort_values("niveau_reel", ascending=False).iloc[0]
    top1_correct = (champion["nom"] == meilleur_vrai["nom"])

    return m["spearman"], m["mae_rank"], top3, top1_correct


# ---------- 2. SIMULATION ROUND-ROBIN ----------

def simuler_un_tournoi_round_robin(seed: int | None = None):
    if seed is not None:
        random.seed(seed)

    joueurs = joueurs_belloy()
    tournoi = Tournoi(participants=joueurs, match=match("NIVEAU"))

    n = len(joueurs)
    matchs = []
    for i in range(n):
        for j in range(i + 1, n):
            matchs.append((joueurs[i], joueurs[j]))
    random.shuffle(matchs)

    for j1, j2 in matchs:
        resultat = tournoi.match.resultat(j1, j2)

        if resultat == J1_GAGNE:
            tournoi.resultats[j1.nom] += 1
        elif resultat == J2_GAGNE:
            tournoi.resultats[j2.nom] += 1

    df_last = pd.DataFrame({
        "nom": [j.nom for j in joueurs],
        "niveau_reel": [getattr(j, "niveau", None) for j in joueurs],
        "elo": [j.elo for j in joueurs],
        "score": [tournoi.resultats[j.nom] for j in joueurs],
    })
    df_last = rank_round(df_last)

    m = metrics(df_last)
    top3 = topk_accuracy(df_last, k=3)

    df_sorted_rank = df_last.sort_values("rang")
    champion = df_sorted_rank.iloc[0]
    meilleur_vrai = df_last.sort_values("niveau_reel", ascending=False).iloc[0]
    top1_correct = (champion["nom"] == meilleur_vrai["nom"])

    return m["spearman"], m["mae_rank"], top3, top1_correct


# ---------- 3. BOUCLES D’EXPÉRIENCES GLOBALES ----------

def run_experiences(n_experiences, nb_rondes):
    spearmans, maes, top3s = [], [], []
    top1_corrects = 0

    for t in range(n_experiences):
        s, mae, top3, top1_ok = simuler_un_tournoi(nb_rondes, seed=t)
        spearmans.append(s)
        maes.append(mae)
        top3s.append(top3)
        if top1_ok:
            top1_corrects += 1

    print(f"\n=== Résumé sur {n_experiences} tournois de {nb_rondes} rondes ===")
    print(f"Spearman moyen      : {mean(spearmans):.3f} (écart-type {pstdev(spearmans):.3f})")
    print(f"MAE de rang moyenne : {mean(maes):.2f} (écart-type {pstdev(maes):.2f})")
    print(f"Top-3 accuracy moy. : {mean(top3s):.2f}")
    print(f"Top-1 correct       : {top1_corrects}/{n_experiences} = {top1_corrects/n_experiences:.2%}")

    return spearmans, maes, top3s, top1_corrects


def run_experiences_round_robin(n_experiences):
    spearmans, maes, top3s = [], [], []
    top1_corrects = 0

    for t in range(n_experiences):
        s, mae, top3, top1_ok = simuler_un_tournoi_round_robin(seed=t)
        spearmans.append(s)
        maes.append(mae)
        top3s.append(top3)
        if top1_ok:
            top1_corrects += 1

    print(f"\n=== Round-robin : Résumé sur {n_experiences} tournois toutes-rondes ===")
    print(f"Spearman moyen      : {mean(spearmans):.3f} (écart-type {pstdev(spearmans):.3f})")
    print(f"MAE de rang moyenne : {mean(maes):.2f} (écart-type {pstdev(maes):.2f})")
    print(f"Top-3 accuracy moy. : {mean(top3s):.2f}")
    print(f"Top-1 correct       : {top1_corrects}/{n_experiences} = {top1_corrects/n_experiences:.2%}")

    return spearmans, maes, top3s, top1_corrects


# ---------- 4. ANALYSE DU RANG DE MANUEL ----------

def rang_manuel_suisse(nb_rondes: int, seed: int | None = None) -> int:
    if seed is not None:
        random.seed(seed)

    joueurs = joueurs_belloy()
    tournoi = Tournoi(participants=joueurs, match=match("NIVEAU"))

    for r in range(1, nb_rondes + 1):
        tournoi.jouer_ronde(r)

    df_all = snapshots_to_df(tournoi.snapshots)
    dernier = df_all["ronde"].max()
    df_last = rank_round(df_all[df_all["ronde"] == dernier])

    return int(df_last.loc[df_last["nom"] == "MARINI Manuel", "rang"].iloc[0])


def rang_manuel_round_robin(seed: int | None = None) -> int:
    if seed is not None:
        random.seed(seed)

    joueurs = joueurs_belloy()
    tournoi = Tournoi(participants=joueurs, match=match("NIVEAU"))

    n = len(joueurs)
    matchs = []
    for i in range(n):
        for j in range(i + 1, n):
            matchs.append((joueurs[i], joueurs[j]))
    random.shuffle(matchs)

    for j1, j2 in matchs:
        resultat = tournoi.match.resultat(j1, j2)

        if resultat == J1_GAGNE:
            tournoi.resultats[j1.nom] += 1
        elif resultat == J2_GAGNE:
            tournoi.resultats[j2.nom] += 1

    df_last = pd.DataFrame({
        "nom": [j.nom for j in joueurs],
        "niveau_reel": [getattr(j, "niveau", None) for j in joueurs],
        "elo": [j.elo for j in joueurs],
        "score": [tournoi.resultats[j.nom] for j in joueurs],
    })
    df_last = rank_round(df_last)

    return int(df_last.loc[df_last["nom"] == "MARINI Manuel", "rang"].iloc[0])


def distrib_rang_manuel_suisse(nb_rondes: int, n_experiences: int):
    return [rang_manuel_suisse(nb_rondes, seed=t) for t in range(n_experiences)]


def distrib_rang_manuel_round_robin(n_experiences: int):
    return [rang_manuel_round_robin(seed=t) for t in range(n_experiences)]


def print_stats_rangs(label: str, rangs: list[int]):
    c = Counter(rangs)
    n = len(rangs)
    mean_rank = sum(rangs) / n

    print(f"\n=== {label} ===")
    print(f"Nombre de tournois : {n}")
    print(f"Rang moyen de Manuel : {mean_rank:.2f}")

    p1 = c[1] / n
    p_top3 = sum(c[r] for r in [1, 2, 3]) / n
    p_top5 = sum(c[r] for r in [1, 2, 3, 4, 5]) / n

    print(f"Probabilité d'être 1er   : {p1:.3f}")
    print(f"Probabilité d'être top-3 : {p_top3:.3f}")
    print(f"Probabilité d'être top-5 : {p_top5:.3f}")

    print("Répartition par rang (rangs avec au moins 1 occurrence) :")
    for r in sorted(c.keys()):
        print(f"  Rang {r}: {c[r]} tournois ({c[r]/n:.3f})")


def plot_hist_rangs_manuel(rangs, titre):
    plt.figure()
    bins = range(1, 23)
    plt.hist(rangs, bins=bins, align="left", rwidth=0.8)
    plt.xticks(range(1, 22))
    plt.xlabel("Rang final de MARINI Manuel")
    plt.ylabel("Nombre de tournois")
    plt.title(titre)
    plt.tight_layout()
    plt.show()


# ---------- 5. POINT D’ENTRÉE ----------

if 0:# __name__ == "__main__":
    n_exp = 500

    # Exemple : stats sur le rang de Manuel
    rangs_7 = distrib_rang_manuel_suisse(7, n_exp)
    rangs_9 = distrib_rang_manuel_suisse(9, n_exp)
    rangs_11 = distrib_rang_manuel_suisse(11, n_exp)
    rangs_rr = distrib_rang_manuel_round_robin(n_exp)

    print_stats_rangs("Suisse 7 rondes", rangs_7)
    print_stats_rangs("Suisse 9 rondes", rangs_9)
    print_stats_rangs("Suisse 11 rondes", rangs_11)
    print_stats_rangs("Round-robin complet", rangs_rr)

    plot_hist_rangs_manuel(rangs_7, "Suisse 7 rondes - Rang de Manuel")
    plot_hist_rangs_manuel(rangs_9, "Suisse 9 rondes - Rang de Manuel")
    plot_hist_rangs_manuel(rangs_11, "Suisse 11 rondes - Rang de Manuel")
    plot_hist_rangs_manuel(rangs_rr, "Round-robin complet - Rang de Manuel")




# ---------- 6. PLOT TOURNOI ----------


def plot_distributions_tournoi(tournoi_selectionne, savefig=False, folder="plots"):
    n = 500

    data = {
        "Uniforme": creer_joueurs_uniformes(n),
        "Gaussienne": creer_joueurs_gaussiens(n),
        "Bimodale": creer_joueurs_bimodaux(n),
        "Asymétrique": creer_joueurs_asymetriques(n),
        "Anormale": creer_joueurs_anormale(n),
        "Remontada": creer_joueurs_remontada(n),
        "Gaussiens_elo_identique": creer_joueurs_gaussiens_elo(n, bool_elo_depart_identique=True),
        "Gaussiens_elo_aleatoire": creer_joueurs_gaussiens_elo(n, bool_elo_depart_identique=False)
    }

    if savefig:
        os.makedirs(folder, exist_ok=True)

    for name, joueurs in data.items():
        niveaux = np.array([j.niveau_E for j in joueurs])
        elos = np.array([j.elo for j in joueurs])

        idx = np.argsort(niveaux)
        niveaux_trie = niveaux[idx]
        elos_trie = elos[idx]


        # --- lancement d’un tournoi ---
        tournoi = Tournoi(participants=joueurs, match=match("NIVEAU"))
        
        # Vérifie que la méthode existe
        if not hasattr(tournoi, tournoi_selectionne):
            raise ValueError(f"La méthode '{tournoi_selectionne}' n'existe pas dans l'objet Tournoi.")

        # Appel dynamique de la méthode
        methode = getattr(tournoi, tournoi_selectionne)
        classement = methode()  # le classement est une liste de liste [[les 1er si égalités], [ les 2imes], [ les 3ièmes] ...]

        joueurs_aplatis = []
        rang_values = []

        for i, sous_liste in enumerate(classement):
            # rang = plus petit pour le vainqueur
            rang = len(classement) - 1 - i  # inverse l'ordre
            for j in sous_liste:
                joueurs_aplatis.append(j)
                rang_values.append(rang)

        rang_values = np.array(rang_values)

        # Suite du code : histogrammes, plots, Spearman, etc.
                
        niveaux_cl = np.array([j.niveau_E for j in joueurs_aplatis])
        elos_cl = np.array([j.elo for j in joueurs_aplatis])


        # Spearman niveau→rang et elo→rang
        spearman_niv = np.corrcoef(np.argsort(niveaux_cl), rang_values)[0,1]
        spearman_elo = np.corrcoef(np.argsort(elos_cl), rang_values)[0,1]

        fig, axs = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle(f"{name} (N={n})", fontsize=15)

        c = '#' + ''.join(choices('0123456789ABCDEF', k=6))

        # --- Histogramme ---
        axs[0,0].hist(niveaux, bins=50, color=c, alpha=0.7, edgecolor='black')
        axs[0,0].set_title("Répartition Niveau (Histogramme)")
        axs[0,0].set_ylabel("Nombre de joueurs")
        axs[0,0].grid(axis='y', alpha=0.3)

        # --- Tri Niveau vs Elo ---
        x = range(n)
        axs[0,1].plot(x, niveaux_trie, label="Niveau réel", linewidth=2)
        axs[0,1].plot(x, elos_trie, label="Elo estimé", linewidth=2)
        axs[0,1].fill_between(x, niveaux_trie, elos_trie, alpha=0.2)
        axs[0,1].set_title("Triés - Comparatif Niveau vs Elo")
        axs[0,1].set_ylabel("Valeur")
        axs[0,1].grid(alpha=0.3)
        axs[0,1].legend()

        # --- Elo vs Rang ---
        axs[1,0].scatter(elos_cl, rang_values)
        axs[1,0].invert_yaxis()
        axs[1,0].set_title("Elo → Rang tournoi")
        axs[1,0].set_xlabel("Elo")
        axs[1,0].set_ylabel("Rang (0 = meilleur)")
        axs[1,0].grid(alpha=0.3)
        axs[1,0].text(0.05, 0.9, f"Spearman: {spearman_elo:.3f}", transform=axs[1,0].transAxes)

        # --- Niveau vs Rang ---
        axs[1,1].scatter(niveaux_cl, rang_values)
        axs[1,1].invert_yaxis()
        axs[1,1].set_title("Niveau → Rang tournoi")
        axs[1,1].set_xlabel("Niveau")
        axs[1,1].set_ylabel("Rang (0 = meilleur)")
        axs[1,1].grid(alpha=0.3)
        axs[1,1].text(0.05, 0.9, f"Spearman: {spearman_niv:.3f}", transform=axs[1,1].transAxes)

        plt.tight_layout()

        if savefig:
            path = os.path.join(folder, f"{name}.png")
            plt.savefig(path, dpi=200)

        plt.show()


plot_distributions_tournoi("elimination_direct")
