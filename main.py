from joueur import Joueur
from tournoi import Tournoi


if __name__ == "__main__":
    # 1. Création de quelques joueurs de test
    joueurs = [
        Joueur("Alice", 1600),
        Joueur("Bob", 1550),
        Joueur("Charlie", 1500),
        Joueur("David", 1450),
        Joueur("Emma", 1700),
        Joueur("Fred", 1520),
        Joueur("Gina", 1480),
        Joueur("Hugo", 1650),
    ]

    # 2. Création du tournoi
    tournoi = Tournoi(participants=joueurs, match=None)

    nb_rondes = 10
    for r in range(1, nb_rondes + 1):
        tournoi.jouer_ronde(r, avec_nulles=False)

    print("Résultats finaux après", nb_rondes, "rondes :")
    classement_final = sorted(tournoi.participants, 
                              key=lambda j: (tournoi.resultats[j.nom], j.elo), 
                              reverse=True)
    print("Classement final :")
    for rang, joueur in enumerate(classement_final, start=1):
        score = tournoi.resultats[joueur.nom]
        print(f"{rang}. {joueur.nom} - Score: {score}, ELO: {joueur.elo}")
