import random
import numpy as np
import matplotlib.pyplot as plt

# Tes modules
from joueur import Joueur
from saison import Saison
from metrics import MetricsAnalyzer

# Fixer la graine pour la reproductibilité
random.seed(42)
np.random.seed(42)

def generer_niveaux_fixes(n=32):
    """Génère l'ADN des joueurs (Niveau intrinsèque)."""
    niveaux = []
    for _ in range(n):
        niv = random.gauss(1500, 200)
        niveaux.append(niv)
    return sorted(niveaux)

def creer_population_fraiche(niveaux_adn, elo_depart=1200):
    """Crée des joueurs vierges pour une nouvelle saison."""
    joueurs = []
    for i, niv in enumerate(niveaux_adn):
        j = Joueur(f"J{i:02d}", niveau=niv, elo=elo_depart)
        joueurs.append(j)
    return joueurs

def afficher_tableau_console(metrics_globales, formats, distributions):
    """Affiche le tableau récapitulatif dans la console."""
    print("\n" + "="*140)
    print(f"{'RÉSULTATS MOYENS (Sur l\'ensemble des saisons simulées)':^140}")
    print("="*140)
    
    headers = [
        "Format", "Dist.", "Spearman", "Top3 Acc", "Bot3 Acc", "Volatilité (Rang)", "Robustesse"
    ]
    row_fmt = "{:<12} | {:<14} | {:<12} | {:<10} | {:<10} | {:<18} | {:<20}"
    print(row_fmt.format(*headers))
    print("-" * 140)

    for fmt in formats:
        for dist in distributions:
            key = (fmt, dist)
            data = metrics_globales[key]
            
            m_sp = np.mean(data["spearman"])
            m_top = np.mean(data["top3"])
            m_bot = np.mean(data["bot3"])
            m_vol_mean = np.mean(data["vol_mean"]) 
            m_vol_std = np.mean(data["vol_std"])   
            
            print(row_fmt.format(
                fmt, dist, 
                f"{m_sp:.3f}", 
                f"{m_top:.1%}", 
                f"{m_bot:.1%}", 
                f"{m_vol_mean:.2f}", 
                f"{m_vol_std:.2f}"
            ))
        print("-" * 140)

def afficher_graphes_points_vs_niveau_coherent(player_stats, metrics_globales, formats, distributions, niveaux_adn):
    """
    Affiche une grille de graphiques cohérente.
    AXE Y INVERSÉ : Les points faibles (1er, 2e...) sont en haut.
    MÉTRIQUES INCRUSTÉES : Pour lier l'image aux chiffres.
    """
    n_rows = len(formats)
    n_cols = len(distributions)
    
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(18, 14), sharex=True)
    fig.suptitle("Performance Moyenne & Métriques Clés\n(Points vs Niveau Intrinsèque - Axe Y Inversé)", fontsize=16, y=0.99)

    for i, fmt in enumerate(formats):
        for j, dist in enumerate(distributions):
            # Gestion des axes (cas 1x1, 1xN, Nx1, NxN)
            if n_rows == 1 and n_cols == 1: ax = axs
            elif n_rows == 1: ax = axs[j]
            elif n_cols == 1: ax = axs[i]
            else: ax = axs[i, j]
            
            key = (fmt, dist)
            stats_joueurs = player_stats[key]
            metrics_data = metrics_globales[key]
            
            # 1. Données Points
            X = []
            Y = []
            Y_ERR = [] 

            for idx in range(len(niveaux_adn)):
                X.append(niveaux_adn[idx])
                # On récupère la moyenne des points du joueur sur toutes les saisons
                toutes_saisons_points = [x[0] for x in stats_joueurs[idx]]
                # Et l'écart-type de ses points (pour visualiser s'il a eu des scores très différents)
                toutes_saisons_stds = [x[1] for x in stats_joueurs[idx]]
                
                Y.append(np.mean(toutes_saisons_points))
                Y_ERR.append(np.mean(toutes_saisons_stds))

            # 2. Données Métriques (Moyennes) pour la boîte de texte
            avg_sp = np.mean(metrics_data["spearman"])
            avg_top = np.mean(metrics_data["top3"])
            avg_vol = np.mean(metrics_data["vol_mean"]) # C'est la volatilité du RANG
            
            stats_text = (
                f"Spearman: {avg_sp:.3f}\n"
                f"Top3 Acc: {avg_top:.0%}\n"
                f"Volat.(Rg): {avg_vol:.2f}"
            )

            # 3. Tracé
            # Scatter avec barres d'erreur
            ax.errorbar(X, Y, yerr=Y_ERR, fmt='o', ecolor='gray', elinewidth=1, capsize=2, alpha=0.6, markersize=4, label='Joueurs')
            

            # 4. Boite de texte en haut à gauche
            # transform=ax.transAxes permet de placer par rapport à la boite (0,0 = bas gauche, 1,1 = haut droit)
            # Comme on inverse l'axe Y, "haut" reste visuellement en haut
            props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray')
            ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontsize=9,
                    verticalalignment='top', bbox=props, family='monospace', fontweight='bold')

            # 5. Titres et Axes
            if i == 0: ax.set_title(dist.capitalize(), fontweight='bold', fontsize=14)
            if j == 0: ax.set_ylabel(f"{fmt.upper()}\nPoints Moyens", fontweight='bold', fontsize=12)
            if i == n_rows - 1: ax.set_xlabel("Niveau Intrinsèque")
            
            ax.grid(True, linestyle='--', alpha=0.4)
            
            # IMPORTANT : On inverse l'axe Y.
            # Les petits scores (1er, 2e...) seront en HAUT.
            ax.invert_yaxis()

    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plt.show()

def main():
    # --- PARAMÈTRES ---
    NB_SAISONS = 50      
    NB_TOURNOIS = 5     
    NB_JOUEURS = 32
    ELO_DEPART = 1200
    
    FORMATS = ["suisse", "elimination", "round_robin"]
    DISTRIBUTIONS = ["lineaire", "exponentielle", "logarithmique"]
    
    niveaux_adn = generer_niveaux_fixes(NB_JOUEURS)
    
    # Stockage
    metrics_globales = {}
    player_stats = {}

    for fmt in FORMATS:
        for dist in DISTRIBUTIONS:
            k = (fmt, dist)
            metrics_globales[k] = {
                "spearman": [], "top3": [], "bot3": [], 
                "vol_mean": [], "vol_std": []
            }
            player_stats[k] = {i: [] for i in range(NB_JOUEURS)}

    print(f"=== DÉBUT SIMULATION ({NB_SAISONS} saisons) ===")

    for s in range(NB_SAISONS):
        for fmt in FORMATS:
            # A. Jeu
            population = creer_population_fraiche(niveaux_adn, ELO_DEPART)
            ma_saison = Saison(population)

            for t in range(NB_TOURNOIS):
                ma_saison.jouer_tournoi(fmt)
            
            # B. Analyse
            analyzer = MetricsAnalyzer(population)
            
            for dist in DISTRIBUTIONS:
                key = (fmt, dist)
                
                # Metrics (Calculées sur les Rangs pour la volatilité)
                sp = analyzer.calculate_spearman(dist)
                top, bot = analyzer.top_bottom_accuracy(dist, k=3)
                vol_mean, vol_std = analyzer.volatility_analysis(dist)
                
                metrics_globales[key]["spearman"].append(sp)
                metrics_globales[key]["top3"].append(top)
                metrics_globales[key]["bot3"].append(bot)
                metrics_globales[key]["vol_mean"].append(vol_mean)
                metrics_globales[key]["vol_std"].append(vol_std)
                
                # Points (Pour le graphe)
                for idx, joueur in enumerate(population):
                    historique = joueur.historique_points[dist]
                    if len(historique) > 0:
                        moy = np.mean(historique)
                        std = np.std(historique)
                        player_stats[key][idx].append((moy, std))

        if (s+1) % 10 == 0:
            print(f" -> Saison {s+1}/{NB_SAISONS} terminée.")

    # --- AFFICHAGE ---
    afficher_tableau_console(metrics_globales, FORMATS, DISTRIBUTIONS)
    
    print("\nGénération des graphiques cohérents (Axe Y inversé)...")
    afficher_graphes_points_vs_niveau_coherent(player_stats, metrics_globales, FORMATS, DISTRIBUTIONS, niveaux_adn)

if __name__ == "__main__":
    main()