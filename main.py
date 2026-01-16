import random
import numpy as np
import matplotlib.pyplot as plt

from joueur import Joueur
from saison import Saison
from metrics import MetricsAnalyzer

# --- 1. PARAMÈTRES DE LA SIMULATION ---
NB_SAISONS = 50      # Nombre de répétitions (Monte Carlo)
NB_TOURNOIS = 5     # Longueur d'une saison
NB_JOUEURS = 32
ELO_DEPART = 1200


# Fixer la graine pour la reproductibilité (comparaison ceteris paribus)
random.seed(42)
np.random.seed(42)

def generer_niveaux_fixes(n=32):
    """Génère l'ADN des joueurs (Niveau intrinsèque)."""
    niveaux = []
    for _ in range(n):
        # Distribution Gaussienne (Moy 1500, Std 200)
        niv = random.gauss(1500, 200)
        niveaux.append(niv)
    return sorted(niveaux) # Trié pour des graphes plus lisibles

def creer_population_fraiche(niveaux_adn, elo_depart=1200):
    """Crée des joueurs vierges pour une nouvelle saison."""
    joueurs = []
    for i, niv in enumerate(niveaux_adn):
        j = Joueur(f"J{i:02d}", niveau=niv, elo=elo_depart)
        joueurs.append(j)
    return joueurs

def afficher_tableau_console(metrics_globales, formats, distributions):
    """Affiche le tableau récapitulatif complet."""
    print("\n" + "="*140)
    print(f"{'RÉSULTATS MOYENS (Sur l\'ensemble des saisons simulées)':^140}")
    print("="*140)
    
    headers = [
        "Format", "Dist.", "Spearman", "Top3 Acc", "Bot3 Acc", "Volatilité (Moy)", "Robustesse (Std of Std)"
    ]
    # Formatage de l'entête
    row_fmt = "{:<12} | {:<14} | {:<12} | {:<10} | {:<10} | {:<18} | {:<20}"
    print(row_fmt.format(*headers))
    print("-" * 140)

    for fmt in formats:
        for dist in distributions:
            key = (fmt, dist)
            data = metrics_globales[key]
            
            # Calcul des moyennes
            m_sp = np.mean(data["spearman"])
            m_top = np.mean(data["top3"])
            m_bot = np.mean(data["bot3"])
            m_vol_mean = np.mean(data["vol_mean"]) # Moyenne de la volatilité moyenne
            m_vol_std = np.mean(data["vol_std"])   # Moyenne de la robustesse
            
            print(row_fmt.format(
                fmt, dist, 
                f"{m_sp:.3f}", 
                f"{m_top:.1%}", 
                f"{m_bot:.1%}", 
                f"{m_vol_mean:.2f}", 
                f"{m_vol_std:.2f}"
            ))
        print("-" * 140)

def afficher_graphes_points_vs_niveau(player_stats, formats, distributions, niveaux_adn):
    """
    Affiche une grille de graphiques.
    X = Niveau Intrinsèque
    Y = Points Moyens (ou Elo Final Moyen)
    Barres d'erreur = Écart-type moyen du joueur (sa consistance).
    """
    n_rows = len(formats)
    n_cols = len(distributions)
    
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(20, 15), sharex=True)
    # sharey=False car Elo et Points n'ont pas la même échelle
    
    fig.suptitle("Performance Moyenne : Points/Elo vs Niveau Intrinsèque\n(Barres d'erreur = Écart-type moyen du joueur)", fontsize=16, y=0.99)

    for i, fmt in enumerate(formats):
        for j, dist in enumerate(distributions):
            # Gestion cas 1 seule ligne/colonne
            if n_rows == 1 and n_cols == 1: ax = axs
            elif n_rows == 1: ax = axs[j]
            elif n_cols == 1: ax = axs[i]
            else: ax = axs[i, j]
            
            key = (fmt, dist)
            stats_joueurs = player_stats[key]
            
            X = []
            Y = []
            Y_ERR = [] # Volatilité individuelle moyenne

            # On agrège les données par joueur (index 0 à N)
            for idx in range(len(niveaux_adn)):
                X.append(niveaux_adn[idx])
                
                # stats_joueurs[idx] contient une liste de tuples (moyenne_saison, std_saison)
                # On veut la moyenne globale des points et la moyenne globale de la volatilité
                toutes_saisons_points = [x[0] for x in stats_joueurs[idx]]
                toutes_saisons_stds = [x[1] for x in stats_joueurs[idx]]
                
                Y.append(np.mean(toutes_saisons_points))
                # Ici on affiche la moyenne des écarts-types (la volatilité moyenne du joueur)
                Y_ERR.append(np.mean(toutes_saisons_stds))

            # Plot
            # ecolor='gray' pour les barres d'erreur discrètes
            ax.errorbar(X, Y, yerr=Y_ERR, fmt='o', ecolor='gray', elinewidth=1, capsize=3, alpha=0.8, markersize=5, label='Joueurs')
            

            # Titres et Labels
            if i == 0: ax.set_title(dist.capitalize(), fontweight='bold', fontsize=14)
            if j == 0: ax.set_ylabel(f"{fmt.upper()}\nPoints / Elo", fontweight='bold', fontsize=12)
            if i == n_rows - 1: ax.set_xlabel("Niveau Intrinsèque")
            
            ax.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plt.show()

def main():
    
    # On teste 3 formats
    FORMATS = ["suisse", "elimination", "round_robin"]
    # On teste 4 distributions (dont Elo)
    DISTRIBUTIONS = ["lineaire", "exponentielle", "logarithmique"]
    
    # --- 2. INITIALISATION ---
    niveaux_adn = generer_niveaux_fixes(NB_JOUEURS)
    
    # Stockage des métriques globales (pour le tableau)
    metrics_globales = {}
    
    # Stockage des stats par joueur (pour les graphes)
    # Structure: player_stats[(fmt, dist)][id_joueur] = liste de (points_moyens, ecart_type)
    player_stats = {}

    for fmt in FORMATS:
        for dist in DISTRIBUTIONS:
            k = (fmt, dist)
            metrics_globales[k] = {
                "spearman": [], "top3": [], "bot3": [], 
                "vol_mean": [], "vol_std": []
            }
            player_stats[k] = {i: [] for i in range(NB_JOUEURS)}

    print(f"=== DÉBUT SIMULATION ({NB_SAISONS} saisons de {NB_TOURNOIS} tournois) ===")

    # --- 3. BOUCLE PRINCIPALE ---
    for s in range(NB_SAISONS):
        
        # Pour chaque format, on repart de la même population
        for fmt in FORMATS:
            # A. Reset Population
            population = creer_population_fraiche(niveaux_adn, ELO_DEPART)
            ma_saison = Saison(population)

            # B. Jouer Saison
            for t in range(NB_TOURNOIS):
                ma_saison.jouer_tournoi(fmt)
            
            # C. Analyse Metrics
            analyzer = MetricsAnalyzer(population)
            
            for dist in DISTRIBUTIONS:
                key = (fmt, dist)
                
                # 1. Calculs Métriques Globaux
                sp = analyzer.calculate_spearman(dist)
                top, bot = analyzer.top_bottom_accuracy(dist, k=3)
                # Volatilité : moyenne des stds, et std des stds
                vol_mean, vol_std = analyzer.volatility_analysis(dist)
                
                metrics_globales[key]["spearman"].append(sp)
                metrics_globales[key]["top3"].append(top)
                metrics_globales[key]["bot3"].append(bot)
                metrics_globales[key]["vol_mean"].append(vol_mean)
                metrics_globales[key]["vol_std"].append(vol_std)
                
                # 2. Collecte stats par joueur
                for idx, joueur in enumerate(population):
                    historique = joueur.historique_points[dist]
                    if len(historique) > 0:
                        # Si c'est Elo, on prend le final et la std de l'évolution
                        if dist == "elo":
                             # Pour le graphe Elo, "moyenne" = Elo final, "std" = volatilité historique
                            moy = joueur.elo 
                            std = np.std(historique)
                        else:
                            moy = np.mean(historique)
                            std = np.std(historique)
                        
                        # On stocke le couple (Moyenne, Std) pour cette saison
                        player_stats[key][idx].append((moy, std))

        if (s+1) % 10 == 0:
            print(f" -> Saison {s+1}/{NB_SAISONS} analysée.")

    # --- 4. RÉSULTATS ---
    afficher_tableau_console(metrics_globales, FORMATS, DISTRIBUTIONS)
    
    print("\nGénération des graphiques...")
    afficher_graphes_points_vs_niveau(player_stats, FORMATS, DISTRIBUTIONS, niveaux_adn)

main()