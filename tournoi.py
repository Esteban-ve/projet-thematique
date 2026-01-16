# tournoi.py
import random
from match import Match

class Tournoi:
    def __init__(self, participants):
        """
        :param participants: Liste d'objets Joueur
        """
        self.participants = participants
        
        # --- Structures de données pour le Système Suisse ---
        self.scores = {p: 0.0 for p in participants}      # Score dans le tournoi
        self.deja_joue = {p: set() for p in participants} # Historique des adversaires
        self.a_eu_bye = {p: False for p in participants}  # Gestion des exempts

    # =========================================================
    #  1. ROUND ROBIN (Championnat : Tout le monde vs Tout le monde)
    # =========================================================

    def round_robin(self, return_scores=False):
        """
        Chaque joueur rencontre tous les autres une fois.
        Si return_scores=True, renvoie aussi le score de chaque joueur.
        """
        local_scores = {j: 0 for j in self.participants}
        n = len(self.participants)
        
        for i in range(n):
            for k in range(i + 1, n):
                j1 = self.participants[i]
                j2 = self.participants[k]
                vainqueur = Match.simuler(j1, j2)
                local_scores[vainqueur] += 1
                perdant = j2 if vainqueur == j1 else j1
                Match.update_elo(vainqueur, perdant)
        
        classement = sorted(self.participants, key=lambda j: local_scores[j], reverse=True)
        
        if return_scores:
            return classement, local_scores
        return classement



    # =========================================================
    #  2. DOUBLE ÉLIMINATION (Winner & Loser Brackets)
    # =========================================================

    def _jouer_liste_paires(self, joueurs, seeding_method="high_low"):
        """
        Helper pour jouer une série de matchs dans un bracket.
        Retourne (gagnants, perdants).
        """
        gagnants = []
        perdants = []
        
        joueurs_locaux = joueurs[:] # Copie pour manipulation
        
        # Gestion du Bye si nombre impair (le meilleur passe sans jouer)
        if len(joueurs_locaux) % 2 != 0:
            joueurs_locaux.sort(key=lambda x: x.elo, reverse=True)
            bye = joueurs_locaux.pop(0)
            gagnants.append(bye)

        # Appariements
        paires = []
        n = len(joueurs_locaux)
        
        if seeding_method == "high_low":
            # 1er vs Dernier (Classique Winner Bracket)
            joueurs_locaux.sort(key=lambda x: x.elo, reverse=True)
            for i in range(n // 2):
                paires.append((joueurs_locaux[i], joueurs_locaux[n - 1 - i]))
        elif seeding_method == "random":
            # Aléatoire (Souvent utilisé en Loser Bracket pour varier)
            random.shuffle(joueurs_locaux)
            for i in range(0, n, 2):
                paires.append((joueurs_locaux[i], joueurs_locaux[i+1]))

        # Résolution des matchs
        for j1, j2 in paires:
            vainqueur = Match.simuler(j1, j2)
            perdant = j2 if vainqueur == j1 else j1
            
            Match.update_elo(vainqueur, perdant)
            
            gagnants.append(vainqueur)
            perdants.append(perdant)
            
        return gagnants, perdants

    def double_elimination(self):
        """
        Tournoi à double élimination complet.
        """
        # Initialisation : Tout le monde commence en Winner Bracket (WB)
        winner_bracket = sorted(self.participants, key=lambda j: j.elo, reverse=True)
        loser_bracket = []
        elimines_stack = [] # Pile pour stocker l'ordre d'élimination (du premier au dernier sorti)

        # Boucle principale : tant qu'on n'est pas en finale (1 WB vs 1 LB)
        while len(winner_bracket) > 1 or len(loser_bracket) > 1:
            
            # --- A. Matchs du Winner Bracket ---
            tombes_en_lb = []
            if len(winner_bracket) > 1:
                wb_gagnants, tombes_en_lb = self._jouer_liste_paires(winner_bracket, seeding_method="high_low")
                winner_bracket = wb_gagnants
            
            # --- B. Matchs du Loser Bracket (Survivants) ---
            if len(loser_bracket) > 1:
                lb_gagnants, lb_elimines = self._jouer_liste_paires(loser_bracket, seeding_method="random")
                loser_bracket = lb_gagnants
                elimines_stack.extend(lb_elimines) # Ceux là sont éliminés définitivement

            # --- C. Fusion : Les perdants du WB rejoignent le LB ---
            loser_bracket.extend(tombes_en_lb)
            
            # Sécurité boucle infinie si LB est plein mais WB fini
            if len(winner_bracket) <= 1 and len(loser_bracket) > 1:
                continue 

        # --- D. La Grande Finale ---
        # Il reste 1 gagnant WB (invaincu) et 1 gagnant LB (1 défaite)
        
        # S'il n'y a pas de loser bracket (ex: tournoi à 2 joueurs), cas trivial
        if not loser_bracket:
            return winner_bracket + elimines_stack

        wb_boss = winner_bracket[0]
        lb_boss = loser_bracket[0]
        
        champion = None
        finaliste = None
        
        # Match 1
        v1 = Match.simuler(wb_boss, lb_boss)
        l1 = lb_boss if v1 == wb_boss else wb_boss
        Match.update_elo(v1, l1)
        
        if v1 == wb_boss:
            # Le boss du WB gagne -> Terminé
            champion = wb_boss
            finaliste = lb_boss
        else:
            # Le boss du LB gagne -> Reset Bracket (Match décisif)
            # Car le boss du WB a le droit de perdre une fois
            v2 = Match.simuler(lb_boss, wb_boss)
            l2 = wb_boss if v2 == lb_boss else lb_boss
            Match.update_elo(v2, l2)
            
            champion = v2
            finaliste = l2

        # Construction du classement final
        # [1er, 2eme, 3eme (dernier sorti du stack), 4eme...]
        return [champion, finaliste] + list(reversed(elimines_stack))

    # =========================================================
    #  3. SYSTÈME SUISSE (FIDE Style - Backtracking)
    # =========================================================

    def _trier_joueurs_suisse(self):
        """Tri par Score, puis par Elo."""
        return sorted(self.participants, key=lambda p: (self.scores[p], p.elo), reverse=True)

    def _trouver_appariements_recursive(self, joueurs):
        """Backtracking pour trouver des paires valides sans re-match."""
        if not joueurs:
            return []

        j1 = joueurs[0]
        
        for i in range(1, len(joueurs)):
            j2 = joueurs[i]
            
            # Contrainte : Ne pas avoir déjà joué ensemble
            if j2 not in self.deja_joue[j1]:
                # Essai de cette paire
                reste = joueurs[1:i] + joueurs[i+1:]
                res_suite = self._trouver_appariements_recursive(reste)
                
                if res_suite is not None:
                    return [(j1, j2)] + res_suite
        
        return None # Échec de la branche

    def systeme_suisse(self, n_rondes=5):
        """Tournoi Suisse complet."""
        # Reset des compteurs internes
        self.scores = {p: 0.0 for p in self.participants}
        self.deja_joue = {p: set() for p in self.participants}
        self.a_eu_bye = {p: False for p in self.participants}

        for r in range(n_rondes):
            # 1. Préparation de la liste
            classement = self._trier_joueurs_suisse()
            joueurs_round = classement[:]
            
            # 2. Gestion du Bye
            if len(joueurs_round) % 2 == 1:
                # On cherche le joueur le plus bas n'ayant pas eu de bye
                for i in range(len(joueurs_round)-1, -1, -1):
                    cand = joueurs_round[i]
                    if not self.a_eu_bye[cand]:
                        self.a_eu_bye[cand] = True
                        self.scores[cand] += 1.0
                        joueurs_round.pop(i)
                        break
            
            # 3. Appariement
            paires = self._trouver_appariements_recursive(joueurs_round)
            
            # Fallback si blocage (rare)
            if paires is None:
                paires = []
                while len(joueurs_round) >= 2:
                    paires.append((joueurs_round.pop(0), joueurs_round.pop(0)))

            # 4. Jeu
            for j1, j2 in paires:
                self.deja_joue[j1].add(j2)
                self.deja_joue[j2].add(j1)
                
                vainqueur = Match.simuler(j1, j2)
                perdant = j2 if vainqueur == j1 else j1
                
                Match.update_elo(vainqueur, perdant)
                self.scores[vainqueur] += 1.0

        # Classement final
        return sorted(self.participants, key=lambda p: self.scores[p], reverse=True)


    def classement_avec_rangs(self, participants_tries, scores):
        """
        participants_tries : liste déjà triée (ex: retour de round_robin / systeme_suisse)
        scores : dict {joueur: score}
        
        Retourne un dict du style :
        { 1: [A], 2: [B, C], 4: [D] }
        """
        result = {}
        current_rank = 1
        i = 0
        
        while i < len(participants_tries):
            joueur = participants_tries[i]
            score = scores[joueur]
            
            # groupe de joueurs ayant le même score
            group = [joueur]
            j = i + 1
            while j < len(participants_tries) and scores[participants_tries[j]] == score:
                group.append(participants_tries[j])
                j += 1
            
            result[current_rank] = group
            
            # Le rang suivant saute la taille du groupe
            current_rank += len(group)
            i = j
        
        return result

