import random
from analytics import snapshots_to_df, rank_round, metrics, topk_accuracy
from joueur import Joueur
from tournoi import Tournoi
from statistics import mean, pstdev
import matplotlib.pyplot as plt
import pandas as pd

def simuler_un_tournoi(nb_rondes: int, seed: int | None = None):
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
        tournoi.jouer_ronde(r, avec_nulles=False)

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

def simuler_un_tournoi_round_robin(seed: int | None = None):
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

    # On joue tous les matchs, sans nulles pour l'instant
    for j1, j2 in matchs:
        resultat = tournoi.resultat_match(j1, j2)
        if resultat == 1:      # j1 gagne
            tournoi.resultats[j1.nom] += 1
        elif resultat == -1:    # j2 gagne
            tournoi.resultats[j2.nom] += 1

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


def run_experiences(n_experiences: int, nb_rondes: int):
    spearmans = []
    maes = []
    top3s = []
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
    print(f"Top-1 correct       : {top1_corrects}/{n_experiences} "
          f"= {top1_corrects/n_experiences:.2%}")

    return spearmans, maes, top3s, top1_corrects

def run_experiences_round_robin(n_experiences: int):
    spearmans = []
    maes = []
    top3s = []
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
    print(f"Top-1 correct       : {top1_corrects}/{n_experiences} "
          f"= {top1_corrects/n_experiences:.2%}")

    return spearmans, maes, top3s, top1_corrects

def sweep_rounds(n_experiences: int, liste_nb_rondes):
    """
    Lance run_experiences pour plusieurs valeurs de nb_rondes
    et retourne un tableau de résultats agrégés.
    """
    all_results = []

    for nb_rondes in liste_nb_rondes:
        spearmans, maes, top3s, top1_corrects = run_experiences(n_experiences, nb_rondes)

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


if __name__ == "__main__":
    # On teste plusieurs nombres de rondes sur le même groupe de joueurs
    liste_nb_rondes = [3, 5, 7, 9, 11]
    
    results = sweep_rounds(n_experiences=200, liste_nb_rondes=liste_nb_rondes)

    print("\n=== Résumé par nombre de rondes (système suisse) ===")
    for r in results:
        print(
            f"{r['nb_rondes']} rondes -> "
            f"Spearman moy={r['spearman_moy']:.3f}, "
            f"MAE moy={r['mae_moy']:.2f}, "
            f"Top-1={r['top1_rate']:.2%}, "
            f"Top-3={r['top3_moy']:.2f}"
        )

    plot_rounds_curves(results)

    # Système round-robin complet (tous contre tous)
    spearmans_rr, maes_rr, top3s_rr, top1_rr = run_experiences_round_robin(n_experiences=200)
