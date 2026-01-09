from joueur import Joueur
import numpy as np
import matplotlib.pyplot as plt

def joueurs_belloy():
    """Renvoie la liste des joueurs du Grand Prix de la Somme (Belloy)."""
    return [
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

# -----------------------------------------------------------
# 1. Distribution UNIFORME (La Ligne Droite)
# -----------------------------------------------------------
def creer_joueurs_uniformes(n: int, elo_depart: int = 1200) -> list[Joueur]:
    """Test: La vitesse de convergence sur tout le spectre."""
    joueurs = []
    # Répartition linéaire exacte de 1000 à 2000
    niveaux = np.linspace(1000, 2000, n)
    
    for i, niv in enumerate(niveaux):
        joueurs.append(Joueur(f"J_Unif_{i}", elo=elo_depart, niveau_E=niv))
    return joueurs

# -----------------------------------------------------------
# 2. Distribution GAUSSIENNE (La Cloche - Standard)
# -----------------------------------------------------------
def creer_joueurs_gaussiens(n: int, elo_depart: int = 1200) -> list[Joueur]:
    """Test: La précision dans le 'ventre mou' (là où il y a le plus de monde)."""
    joueurs = []
    # Moyenne 1500, écart-type 300
    niveaux = np.random.normal(1500, 300, n)
    
    for i, niv in enumerate(niveaux):
        joueurs.append(Joueur(f"J_Gauss_{i}", elo=elo_depart, niveau_E=niv))
    return joueurs

# -----------------------------------------------------------
# 3. Distribution BIMODALE (Les Deux Mondes)
# -----------------------------------------------------------
def creer_joueurs_bimodaux(n: int, elo_depart: int = 1200) -> list[Joueur]:
    """Test: La capacité à séparer deux groupes distincts (Débutants vs Confirmés)."""
    joueurs = []
    # Moitié à 1100 (Faibles), Moitié à 1900 (Forts), peu de mélange
    groupe_faible = np.random.normal(1100, 100, int(n/2))
    groupe_fort = np.random.normal(1900, 100, n - int(n/2))
    niveaux = np.concatenate([groupe_faible, groupe_fort])
    
    for i, niv in enumerate(niveaux):
        joueurs.append(Joueur(f"J_Bim_{i}", elo=elo_depart, niveau_E=niv))
    return joueurs

# -----------------------------------------------------------
# 4. Distribution ASYMÉTRIQUE (La Queue de Traîne)
# -----------------------------------------------------------
def creer_joueurs_asymetriques(n: int, elo_depart: int = 1200) -> list[Joueur]:
    """Test: La détection des 'Outliers' (quelques génies parmi une masse de débutants)."""
    joueurs = []
    # Distribution Gamma : Beaucoup de faibles, une longue traîne vers les très forts
    shape, scale = 2.0, 150.0 
    niveaux = 1000 + np.random.gamma(shape, scale, n)
    
    for i, niv in enumerate(niveaux):
        joueurs.append(Joueur(f"J_Asym_{i}", elo=elo_depart, niveau_E=niv))
    return joueurs

# -----------------------------------------------------------
# 5. Distribution ANORMALE (Un individu est d'un niveau complètement différent des autres)
# -----------------------------------------------------------

def creer_joueurs_anormale(n: int, elo_depart: int = 1200) -> list[Joueur]:
    """Test: L'excelent joueur au milieu de la masse, donc il devrait ressortir du lot"""
    joueurs = []
    # Moyenne 1500 (pas important), écart-type 30 (réduit)
    niveaux = np.random.normal(1500, 30, n-1)
    niveaux = np.append(niveaux, np.random.normal(2000, 30))
    
    for i, niv in enumerate(niveaux):
        joueurs.append(Joueur(f"J_Gauss_{i}", elo=elo_depart, niveau_E=niv))
    return joueurs

# -----------------------------------------------------------
# Visualisation pour vérifier
# -----------------------------------------------------------
def visualiser_distributions():
    n = 100
    elo_depart = 1200
    
    # Génération des 4 groupes
    data = [
        ("Uniforme", creer_joueurs_uniformes(n, elo_depart)),
        ("Gaussienne", creer_joueurs_gaussiens(n, elo_depart)),
        ("Bimodale", creer_joueurs_bimodaux(n, elo_depart)),
        ("Asymétrique", creer_joueurs_asymetriques(n, elo_depart)),
        ("Anormale", creer_joueurs_anormale(n, elo_depart))
    ]

    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f"Niveaux Réels des Joueurs (Elo départ fixe: {elo_depart})", fontsize=16)

    for ax, (titre, joueurs) in zip(axs.flat, data):
        # On extrait les niveaux réels et on les trie pour voir la courbe
        niveaux_reels = sorted([j.niveau_E for j in joueurs])
        
        # Courbe des niveaux réels
        ax.plot(niveaux_reels, color='tab:orange', label='Niveau Réel', linewidth=2)
        # Ligne de l'Elo de départ
        ax.axhline(y=elo_depart, color='tab:blue', linestyle='--', label='Elo Départ', linewidth=2)
        
        ax.set_title(titre)
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper left")

    plt.tight_layout()
    plt.show()

# --- Fonction de Visualisation ---
def plot_distributions_histogrammes():
    n = 1000  # Nombre élevé pour avoir de beaux histogrammes
    
    # Création des données
    data = {
        "Uniforme": creer_joueurs_uniformes(n),
        "Gaussienne": creer_joueurs_gaussiens(n),
        "Bimodale": creer_joueurs_bimodaux(n),
        "Asymétrique": creer_joueurs_asymetriques(n),
        "Anormale": creer_joueurs_anormale(n)
    }

    # Configuration de la figure : 4 lignes (distributions), 2 colonnes (types de graphiques)
    fig, axs = plt.subplots(4, 2, figsize=(14, 16))
    fig.suptitle(f"Analyse des Distributions (Population: {n} joueurs)", fontsize=16, y=0.95)
    
    colors = ['#3498db', '#e74c3c', '#9b59b6', '#2ecc71'] # Bleu, Rouge, Violet, Vert

    for i, (name, joueurs) in enumerate(data.items()):
        # Extraction des niveaux réels
        niveaux = [j.niveau_E for j in joueurs]
        niveaux_trie = sorted(niveaux)
        c = colors[i]

        # -------------------------------------------------------
        # COLONNE 1 : Histogramme de Fréquence (La Répartition)
        # -------------------------------------------------------
        # "Combien de joueurs sont à ce niveau ?"
        axs[i, 0].hist(niveaux, bins=50, color=c, alpha=0.7, edgecolor='black')
        axs[i, 0].set_title(f"{name} - Répartition (Densité)", fontweight='bold')
        axs[i, 0].set_ylabel("Nombre de Joueurs")
        axs[i, 0].grid(axis='y', alpha=0.3)

        # -------------------------------------------------------
        # COLONNE 2 : Valeurs Triées (La Pente)
        # -------------------------------------------------------
        # "Quelle est la courbe de progression du niveau ?"
        x = range(len(niveaux_trie))
        # On utilise fill_between pour faire un effet "histogramme plein"
        axs[i, 1].fill_between(x, 0, niveaux_trie, color=c, alpha=0.6)
        axs[i, 1].plot(x, niveaux_trie, color=c, linewidth=2) # Ligne du dessus plus forte
        
        axs[i, 1].set_title(f"{name} - Joueurs Triés (Du - fort au + fort)", fontweight='bold')
        axs[i, 1].set_ylabel("Niveau Réel")
        axs[i, 1].set_ylim(bottom=0, top=max(niveaux_trie)*1.1)
        axs[i, 1].grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Ajustement pour le titre principal
    plt.show()


plot_distributions_histogrammes()
visualiser_distributions()