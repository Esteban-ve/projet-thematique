import random
from analytics import snapshots_to_df, rank_round, metrics, topk_accuracy
from joueur import Joueur
from tournoi import Tournoi
from statistics import mean, pstdev
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter
from tournoi import J1_GAGNE, J2_GAGNE, MATCH_NUL

def simuler_un_tournoi(nb_rondes, seed, avec_nulles=True):
    """Simule un tournoi suisse et renvoie les métriques clés + info sur le champion."""
    if seed is not None:
        random.seed(seed)

    joueurs = [
    Joueur("BONNAY Yanis", 1310),
    Joueur("CAERELS Arsene", 950),
    Joueur("CAERELS Basile", 880),
    Joueur("CAILLY Leo", 1480),
    Joueur("CARDON Julia", 1080),
    Joueur("COURTOIS Regis", 1772),
    Joueur("DEVAL Clement", 1486),
    Joueur("DUMEIGE Lucas", 999),
    Joueur("DUMEIGE Mathieu", 1199),
    Joueur("GAMBIER Thibaut", 1350),
    Joueur("GAUMET Philippe", 1624),
    Joueur("GUINET Auguste", 999),
    Joueur("KOTWICA Arthur", 799),
    Joueur("LANDAZURI Fernando", 1567),
    Joueur("LEBLANC Francois", 1594),
    Joueur("MABILLE Philippe", 1300),
    Joueur("MARINI Jeremy", 1423),
    Joueur("MARINI Manuel", 1820),
    Joueur("MARINI Timothee", 1533),
    Joueur("TERNISIEN Jean-Michel", 1464),
    Joueur("VAST Maxence", 1489),
]


    tournoi = Tournoi(participants=joueurs, match=None)

    for r in range(1, nb_rondes + 1):
        tournoi.jouer_ronde(r, avec_nulles=avec_nulles)

    # on reconstruit le DataFrame à partir des snapshots
    df_all = snapshots_to_df(tournoi.snapshots)
    dernier = df_all["ronde"].max()
    df_last = rank_round(df_all[df_all["ronde"] == dernier])

    m = metrics(df_last)
    top3 = topk_accuracy(df_last, k=3)

    # champion et meilleur joueur réel
    df_sorted_rank = df_last.sort_values("rang")
    champion = df_sorted_rank.iloc[0]
    meilleur_vrai = df_last.sort_values("niveau_reel", ascending=False).iloc[0]
    top1_correct = (champion["nom"] == meilleur_vrai["nom"])

    return m["spearman"], m["mae_rank"], top3, top1_correct

def simuler_un_tournoi_round_robin(seed: int | None = None, avec_nulles = False):
    """
    Simule un tournoi toutes-rondes (round-robin) avec les mêmes joueurs que Belloy :
    - chaque joueur rencontre tous les autres exactement une fois ;
    - on utilise Tournoi.resultat_match pour mettre à jour les Elo ;
    - on calcule les mêmes métriques que pour le système suisse.
    """
    if seed is not None:
        random.seed(seed)

    # Même liste de joueurs que pour le suisse
    joueurs = [
        Joueur("BONNAY Yanis", 1310),
        Joueur("CAERELS Arsene", 950),
        Joueur("CAERELS Basile", 880),
        Joueur("CAILLY Leo", 1480),
        Joueur("CARDON Julia", 1080),
        Joueur("COURTOIS Regis", 1772),
        Joueur("DEVAL Clement", 1486),
        Joueur("DUMEIGE Lucas", 999),
        Joueur("DUMEIGE Mathieu", 1199),
        Joueur("GAMBIER Thibaut", 1350),
        Joueur("GAUMET Philippe", 1624),
        Joueur("GUINET Auguste", 999),
        Joueur("KOTWICA Arthur", 799),
        Joueur("LANDAZURI Fernando", 1567),
        Joueur("LEBLANC Francois", 1594),
        Joueur("MABILLE Philippe", 1300),
        Joueur("MARINI Jeremy", 1423),
        Joueur("MARINI Manuel", 1820),
        Joueur("MARINI Timothee", 1533),
        Joueur("TERNISIEN Jean-Michel", 1464),
        Joueur("VAST Maxence", 1489),
    ]


    tournoi = Tournoi(participants=joueurs, match=None)

    # Génération de tous les duels possibles i < j
    n = len(joueurs)
    matchs = []
    for i in range(n):
        for j in range(i + 1, n):
            matchs.append((joueurs[i], joueurs[j]))

    # Mélange de l'ordre des matchs (aléa de calendrier)
    random.shuffle(matchs)

    for j1, j2 in matchs:
        if avec_nulles:
            resultat = tournoi.match_avec_egalite(j1, j2)
        else:
            resultat = tournoi.resultat_match(j1, j2)

        if resultat == J1_GAGNE:
            tournoi.resultats[j1.nom] += 1
        elif resultat == J2_GAGNE:
            tournoi.resultats[j2.nom] += 1
        elif resultat == MATCH_NUL:
            tournoi.resultats[j1.nom] += 0.5
            tournoi.resultats[j2.nom] += 0.5
    # Construction du DataFrame final (analogue à df_last pour le suisse)
    df_last = pd.DataFrame({
        "nom": [j.nom for j in joueurs],
        "niveau_reel": [getattr(j, "_niveau", None) for j in joueurs],
        "elo": [j.elo for j in joueurs],
        "score": [tournoi.resultats[j.nom] for j in joueurs],
    })

    # On trie et on ajoute le rang via ton rank_round
    df_last = rank_round(df_last)

    # Métriques d'équité
    m = metrics(df_last)
    top3 = topk_accuracy(df_last, k=3)

    df_sorted_rank = df_last.sort_values("rang")
    champion = df_sorted_rank.iloc[0]
    meilleur_vrai = df_last.sort_values("niveau_reel", ascending=False).iloc[0]
    top1_correct = (champion["nom"] == meilleur_vrai["nom"])

    return m["spearman"], m["mae_rank"], top3, top1_correct


def run_experiences(n_experiences, nb_rondes, avec_nulles=False):
    spearmans = []
    maes = []
    top3s = []
    top1_corrects = 0

    for t in range(n_experiences):
        s, mae, top3, top1_ok = simuler_un_tournoi(nb_rondes, seed=t, avec_nulles=avec_nulles)
        spearmans.append(s)
        maes.append(mae)
        top3s.append(top3)
        if top1_ok:
            top1_corrects += 1

    print(f"\n=== Résumé sur {n_experiences} tournois de {nb_rondes} rondes ===")
    print(f"Spearman moyen      : {mean(spearmans):.3f} (écart-type {pstdev(spearmans):.3f})")
    print(f"MAE de rang moyenne : {mean(maes):.2f} (écart-type {pstdev(maes):.2f})")
    print(f"Top-3 accuracy moy. : {mean(top3s):.2f}")
    print(f"Top-1 correct       : {top1_corrects}/{n_experiences} "
          f"= {top1_corrects/n_experiences:.2%}")

    return spearmans, maes, top3s, top1_corrects

def run_experiences_round_robin(n_experiences, avec_nulles=False):
    spearmans = []
    maes = []
    top3s = []
    top1_corrects = 0

    for t in range(n_experiences):
        s, mae, top3, top1_ok = simuler_un_tournoi_round_robin(seed=t, avec_nulles=avec_nulles)
        spearmans.append(s)
        maes.append(mae)
        top3s.append(top3)
        if top1_ok:
            top1_corrects += 1

    print(f"\n=== Round-robin : Résumé sur {n_experiences} tournois toutes-rondes ===")
    print(f"Spearman moyen      : {mean(spearmans):.3f} (écart-type {pstdev(spearmans):.3f})")
    print(f"MAE de rang moyenne : {mean(maes):.2f} (écart-type {pstdev(maes):.2f})")
    print(f"Top-3 accuracy moy. : {mean(top3s):.2f}")
    print(f"Top-1 correct       : {top1_corrects}/{n_experiences} "
          f"= {top1_corrects/n_experiences:.2%}")

    return spearmans, maes, top3s, top1_corrects

def sweep_rounds(n_experiences: int, liste_nb_rondes, avec_nulles=False):
    """
    Lance run_experiences pour plusieurs valeurs de nb_rondes
    et retourne un tableau de résultats agrégés.
    """
    all_results = []

    for nb_rondes in liste_nb_rondes:
        spearmans, maes, top3s, top1_corrects = run_experiences(n_experiences, nb_rondes, avec_nulles=avec_nulles)

        all_results.append({
            "nb_rondes": nb_rondes,
            "spearman_moy": mean(spearmans),
            "spearman_std": pstdev(spearmans),
            "mae_moy": mean(maes),
            "mae_std": pstdev(maes),
            "top3_moy": mean(top3s),
            "top1_rate": top1_corrects / n_experiences,
        })

    return all_results


def plot_spearman_hist(spearmans):
    plt.figure()
    plt.hist(spearmans, bins=15)
    plt.axvline(sum(spearmans)/len(spearmans))
    plt.xlabel("Corrélation de Spearman (force vs classement)")
    plt.ylabel("Nombre de tournois")
    plt.title("Distribution de la qualité du classement (200 tournois suisses)")
    plt.tight_layout()
    plt.show()

def plot_mae_hist(maes):
    plt.figure()
    plt.hist(maes, bins=15)
    plt.axvline(sum(maes)/len(maes))
    plt.xlabel("Erreur moyenne de rang (MAE)")
    plt.ylabel("Nombre de tournois")
    plt.title("Précision du classement en nombre de places")
    plt.tight_layout()
    plt.show()

def plot_mae_box(maes):
    plt.figure()
    plt.boxplot(maes)
    plt.ylabel("Erreur moyenne de rang (MAE)")
    plt.title("Variabilité de l’erreur de classement")
    plt.tight_layout()
    plt.show()

def plot_top_acc(top3s, top1_corrects, n_experiences):
    top1_rate = top1_corrects / n_experiences
    top3_mean = sum(top3s) / len(top3s)

    categories = ["Top-1 (champion correct)", "Top-3 accuracy"]
    values = [top1_rate, top3_mean]

    plt.figure()
    plt.bar(categories, values)
    plt.ylim(0, 1)
    plt.ylabel("Proportion")
    plt.title("Capacité du système à identifier les meilleurs joueurs")
    plt.tight_layout()
    plt.show()

def plot_rounds_curves(results):
    """
    results = liste de dicts renvoyée par sweep_rounds
    Trace Spearman moyen et MAE moyenne en fonction du nombre de rondes.
    """
    xs = [r["nb_rondes"] for r in results]
    spearman_moy = [r["spearman_moy"] for r in results]
    mae_moy = [r["mae_moy"] for r in results]

    # Courbe Spearman moyen
    plt.figure()
    plt.plot(xs, spearman_moy, marker="o")
    plt.xlabel("Nombre de rondes")
    plt.ylabel("Spearman moyen")
    plt.title("Fidélité au niveau réel selon le nombre de rondes")
    plt.tight_layout()
    plt.show()

    # Courbe MAE moyen
    plt.figure()
    plt.plot(xs, mae_moy, marker="o")
    plt.xlabel("Nombre de rondes")
    plt.ylabel("Erreur moyenne de rang (MAE)")
    plt.title("Erreur de classement selon le nombre de rondes")
    plt.tight_layout()
    plt.show()
def plot_comparaison_suisse(
    res_suisse_no,
    res_suisse_with,
    spearman_rr_no=None,
    mae_rr_no=None,
    spearman_rr_with=None,
    mae_rr_with=None,
):
    """
    Compare :
    - système suisse sans nulles
    - système suisse avec nulles
    - éventuellement round-robin (lignes horizontales)
    en termes de Spearman moyen et MAE moyen.
    """
    xs = [r["nb_rondes"] for r in res_suisse_no]

    spearman_no = [r["spearman_moy"] for r in res_suisse_no]
    spearman_with = [r["spearman_moy"] for r in res_suisse_with]
    mae_no = [r["mae_moy"] for r in res_suisse_no]
    mae_with = [r["mae_moy"] for r in res_suisse_with]

    # ---- Spearman ----
    plt.figure()
    plt.plot(xs, spearman_no, marker="o", label="Suisse sans nulles")
    plt.plot(xs, spearman_with, marker="o", linestyle="--", label="Suisse avec nulles")

    # Lignes horizontales pour le round-robin (si fournis)
    if spearman_rr_no is not None:
        plt.axhline(spearman_rr_no, linestyle=":", label="Round-robin sans nulles")
    if spearman_rr_with is not None:
        plt.axhline(spearman_rr_with, linestyle="-.", label="Round-robin avec nulles")

    plt.xlabel("Nombre de rondes")
    plt.ylabel("Spearman moyen")
    plt.title("Fidélité au niveau réel : suisse vs round-robin")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # ---- MAE ----
    plt.figure()
    plt.plot(xs, mae_no, marker="o", label="Suisse sans nulles")
    plt.plot(xs, mae_with, marker="o", linestyle="--", label="Suisse avec nulles")

    if mae_rr_no is not None:
        plt.axhline(mae_rr_no, linestyle=":", label="Round-robin sans nulles")
    if mae_rr_with is not None:
        plt.axhline(mae_rr_with, linestyle="-.", label="Round-robin avec nulles")

    plt.xlabel("Nombre de rondes")
    plt.ylabel("Erreur moyenne de rang (MAE)")
    plt.title("Erreur de classement : suisse vs round-robin")
    plt.legend()
    plt.tight_layout()
    plt.show()

def rang_manuel_suisse(nb_rondes: int, seed: int | None = None, avec_nulles: bool = False) -> int:
    """Renvoie le rang final de MARINI Manuel dans un tournoi suisse simulé."""
    if seed is not None:
        random.seed(seed)

    joueurs = [
        Joueur("BONNAY Yanis", 1310),
        Joueur("CAERELS Arsene", 950),
        Joueur("CAERELS Basile", 880),
        Joueur("CAILLY Leo", 1480),
        Joueur("CARDON Julia", 1080),
        Joueur("COURTOIS Regis", 1772),
        Joueur("DEVAL Clement", 1486),
        Joueur("DUMEIGE Lucas", 999),
        Joueur("DUMEIGE Mathieu", 1199),
        Joueur("GAMBIER Thibaut", 1350),
        Joueur("GAUMET Philippe", 1624),
        Joueur("GUINET Auguste", 999),
        Joueur("KOTWICA Arthur", 799),
        Joueur("LANDAZURI Fernando", 1567),
        Joueur("LEBLANC Francois", 1594),
        Joueur("MABILLE Philippe", 1300),
        Joueur("MARINI Jeremy", 1423),
        Joueur("MARINI Manuel", 1820),
        Joueur("MARINI Timothee", 1533),
        Joueur("TERNISIEN Jean-Michel", 1464),
        Joueur("VAST Maxence", 1489),
    ]

    tournoi = Tournoi(participants=joueurs, match=None)

    for r in range(1, nb_rondes + 1):
        tournoi.jouer_ronde(r, avec_nulles=avec_nulles)

    # On reconstruit le classement final
    df_all = snapshots_to_df(tournoi.snapshots)
    dernier = df_all["ronde"].max()
    df_last = rank_round(df_all[df_all["ronde"] == dernier])

    rang_manuel = int(
        df_last.loc[df_last["nom"] == "MARINI Manuel", "rang"].iloc[0]
    )
    return rang_manuel


def rang_manuel_round_robin(seed: int | None = None, avec_nulles: bool = False) -> int:
    """Renvoie le rang final de MARINI Manuel dans un round-robin simulé."""
    if seed is not None:
        random.seed(seed)

    joueurs = [
        Joueur("BONNAY Yanis", 1310),
        Joueur("CAERELS Arsene", 950),
        Joueur("CAERELS Basile", 880),
        Joueur("CAILLY Leo", 1480),
        Joueur("CARDON Julia", 1080),
        Joueur("COURTOIS Regis", 1772),
        Joueur("DEVAL Clement", 1486),
        Joueur("DUMEIGE Lucas", 999),
        Joueur("DUMEIGE Mathieu", 1199),
        Joueur("GAMBIER Thibaut", 1350),
        Joueur("GAUMET Philippe", 1624),
        Joueur("GUINET Auguste", 999),
        Joueur("KOTWICA Arthur", 799),
        Joueur("LANDAZURI Fernando", 1567),
        Joueur("LEBLANC Francois", 1594),
        Joueur("MABILLE Philippe", 1300),
        Joueur("MARINI Jeremy", 1423),
        Joueur("MARINI Manuel", 1820),
        Joueur("MARINI Timothee", 1533),
        Joueur("TERNISIEN Jean-Michel", 1464),
        Joueur("VAST Maxence", 1489),
    ]

    tournoi = Tournoi(participants=joueurs, match=None)

    # Round-robin : tous les matchs i<j
    n = len(joueurs)
    matchs = []
    for i in range(n):
        for j in range(i + 1, n):
            matchs.append((joueurs[i], joueurs[j]))
    random.shuffle(matchs)

    for j1, j2 in matchs:
        if avec_nulles:
            resultat = tournoi.match_avec_egalite(j1, j2)
        else:
            resultat = tournoi.resultat_match(j1, j2)

        if resultat == J1_GAGNE:
            tournoi.resultats[j1.nom] += 1
        elif resultat == J2_GAGNE:
            tournoi.resultats[j2.nom] += 1
        elif resultat == MATCH_NUL:
            tournoi.resultats[j1.nom] += 0.5
            tournoi.resultats[j2.nom] += 0.5

    df_last = pd.DataFrame({
        "nom": [j.nom for j in joueurs],
        "niveau_reel": [getattr(j, "_niveau", None) for j in joueurs],
        "elo": [j.elo for j in joueurs],
        "score": [tournoi.resultats[j.nom] for j in joueurs],
    })
    df_last = rank_round(df_last)

    rang_manuel = int(
        df_last.loc[df_last["nom"] == "MARINI Manuel", "rang"].iloc[0]
    )
    return rang_manuel

def distrib_rang_manuel_suisse(nb_rondes: int, n_experiences: int, avec_nulles: bool = False):
    rangs = []
    for t in range(n_experiences):
        r = rang_manuel_suisse(nb_rondes, seed=t, avec_nulles=avec_nulles)
        rangs.append(r)
    return rangs


def distrib_rang_manuel_round_robin(n_experiences: int, avec_nulles: bool = False):
    rangs = []
    for t in range(n_experiences):
        r = rang_manuel_round_robin(seed=t, avec_nulles=avec_nulles)
        rangs.append(r)
    return rangs

def print_stats_rangs(label: str, rangs: list[int]):
    c = Counter(rangs)
    n = len(rangs)
    mean_rank = sum(rangs) / n

    print(f"\n=== {label} ===")
    print(f"Nombre de tournois : {n}")
    print(f"Rang moyen de Manuel : {mean_rank:.2f}")

    # Probabilité d'être 1er, top-3, top-5
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
    # 21 joueurs → rangs de 1 à 21
    bins = range(1, 23)  # 1..22 pour inclure 21
    plt.hist(rangs, bins=bins, align="left", rwidth=0.8)
    plt.xticks(range(1, 22))
    plt.xlabel("Rang final de MARINI Manuel")
    plt.ylabel("Nombre de tournois")
    plt.title(titre)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    n_exp = 500  # ou 200 si tu veux que ça tourne plus vite

    # On regarde le cas sans nulles pour commencer
    rangs_7  = distrib_rang_manuel_suisse(7,  n_exp, avec_nulles=False)
    rangs_9  = distrib_rang_manuel_suisse(9,  n_exp, avec_nulles=False)
    rangs_11 = distrib_rang_manuel_suisse(11, n_exp, avec_nulles=False)
    rangs_rr = distrib_rang_manuel_round_robin(n_exp, avec_nulles=False)

    # Stats texte
    print_stats_rangs("Suisse 7 rondes (sans nulles)",  rangs_7)
    print_stats_rangs("Suisse 9 rondes (sans nulles)",  rangs_9)
    print_stats_rangs("Suisse 11 rondes (sans nulles)", rangs_11)
    print_stats_rangs("Round-robin complet (sans nulles)", rangs_rr)

    # Plots
    plot_hist_rangs_manuel(rangs_7,  "Suisse 7 rondes - Rang de Manuel")
    plot_hist_rangs_manuel(rangs_9,  "Suisse 9 rondes - Rang de Manuel")
    plot_hist_rangs_manuel(rangs_11, "Suisse 11 rondes - Rang de Manuel")
    plot_hist_rangs_manuel(rangs_rr, "Round-robin complet - Rang de Manuel")
