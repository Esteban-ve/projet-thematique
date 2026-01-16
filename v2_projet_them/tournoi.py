import random
from match import Match

class Tournoi:
    def __init__(self, participants):
        """
        :param participants: Liste d'objets Joueur
        """
        self.participants = participants
        
        # --- Structures pour le Suisse ---
        self.scores = {p: 0.0 for p in participants}
        self.deja_joue = {p: set() for p in participants}
        self.a_eu_bye = {p: False for p in participants}

    # =========================================================
    #  UTILITAIRES BRACKETS (Double Elim)
    # =========================================================
    
    def _jouer_liste_paires(self, joueurs, seeding_method="high_low"):
        """Joue un round de bracket et renvoie (gagnants, perdants)."""
        gagnants = []
        perdants = []
        
        joueurs_locaux = joueurs[:]
        
        # Gestion Bye (Nombre impair)
        if len(joueurs_locaux) % 2 != 0:
            joueurs_locaux.sort(key=lambda x: x.elo, reverse=True)
            bye = joueurs_locaux.pop(0)
            gagnants.append(bye)

        # Appariements
        paires = []
        n = len(joueurs_locaux)
        
        if seeding_method == "high_low":
            joueurs_locaux.sort(key=lambda x: x.elo, reverse=True)
            for i in range(n // 2):
                paires.append((joueurs_locaux[i], joueurs_locaux[n - 1 - i]))
        elif seeding_method == "random":
            random.shuffle(joueurs_locaux)
            for i in range(0, n, 2):
                paires.append((joueurs_locaux[i], joueurs_locaux[i+1]))

        # Jeu
        for j1, j2 in paires:
            vainqueur = Match.simuler(j1, j2)
            perdant = j2 if vainqueur == j1 else j1
            
            Match.update_elo(vainqueur, perdant)
            
            gagnants.append(vainqueur)
            perdants.append(perdant)
            
        return gagnants, perdants

    # =========================================================
    #  1. DOUBLE ÉLIMINATION (Gestion Ex-Aequo)
    # =========================================================

    def double_elimination(self):
        """
        Renvoie un classement structuré : [[1er], [2e], [3e, 3e], ...]
        """
        winner_bracket = sorted(self.participants, key=lambda j: j.elo, reverse=True)
        loser_bracket = []
        
        # Pile de listes (chaque élément est un GROUPE de joueurs éliminés au même tour)
        elimines_stack = [] 

        while len(winner_bracket) > 1 or len(loser_bracket) > 1:
            
            # A. Winner Bracket
            tombes_en_lb = []
            if len(winner_bracket) > 1:
                wb_gagnants, tombes_en_lb = self._jouer_liste_paires(winner_bracket, seeding_method="high_low")
                winner_bracket = wb_gagnants
            
            # B. Loser Bracket
            if len(loser_bracket) > 1:
                lb_gagnants, lb_elimines = self._jouer_liste_paires(loser_bracket, seeding_method="random")
                loser_bracket = lb_gagnants
                
                # IMPORTANT : On ajoute le groupe entier (ex-aequo)
                if lb_elimines:
                    elimines_stack.append(lb_elimines)

            # C. Fusion
            loser_bracket.extend(tombes_en_lb)
            
            if len(winner_bracket) <= 1 and len(loser_bracket) > 1:
                continue 

        # D. Grande Finale
        if not loser_bracket:
            # Cas trivial
            return [[winner_bracket[0]]] + list(reversed(elimines_stack))

        wb_boss = winner_bracket[0]
        lb_boss = loser_bracket[0]
        
        champion = None
        finaliste = None
        
        # Match 1
        v1 = Match.simuler(wb_boss, lb_boss)
        l1 = lb_boss if v1 == wb_boss else wb_boss
        Match.update_elo(v1, l1)
        
        if v1 == wb_boss:
            champion = wb_boss
            finaliste = lb_boss
        else:
            # Reset
            v2 = Match.simuler(lb_boss, wb_boss)
            l2 = wb_boss if v2 == lb_boss else lb_boss
            Match.update_elo(v2, l2)
            champion = v2
            finaliste = l2

        # On retourne une structure [[1er], [2e], [3e groupe], [4e groupe]...]
        return [[champion], [finaliste]] + list(reversed(elimines_stack))

    # =========================================================
    #  2. ROUND ROBIN
    # =========================================================

    def round_robin(self):
        local_scores = {j: 0 for j in self.participants}
        n = len(self.participants)
        for i in range(n):
            for k in range(i + 1, n):
                j1, j2 = self.participants[i], self.participants[k]
                vainqueur = Match.simuler(j1, j2)
                perdant = j2 if vainqueur == j1 else j1
                Match.update_elo(vainqueur, perdant)
                local_scores[vainqueur] += 1
        
        # Retourne une liste plate (pas de gestion fine ex-aequo ici pour simplifier le code)
        return sorted(self.participants, key=lambda j: (local_scores[j], j.elo), reverse=True)

    # =========================================================
    #  3. SYSTÈME SUISSE
    # =========================================================

    def _trier_joueurs_suisse(self):
        return sorted(self.participants, key=lambda p: (self.scores[p], p.elo), reverse=True)

    def _trouver_appariements_recursive(self, joueurs):
        if not joueurs: return []
        j1 = joueurs[0]
        for i in range(1, len(joueurs)):
            j2 = joueurs[i]
            if j2 not in self.deja_joue[j1]:
                reste = joueurs[1:i] + joueurs[i+1:]
                res = self._trouver_appariements_recursive(reste)
                if res is not None: return [(j1, j2)] + res
        return None

    def systeme_suisse(self, n_rondes=11):
        self.scores = {p: 0.0 for p in self.participants}
        self.deja_joue = {p: set() for p in self.participants}
        self.a_eu_bye = {p: False for p in self.participants}

        for r in range(n_rondes):
            classement = self._trier_joueurs_suisse()
            joueurs_round = classement[:]
            
            # Gestion Bye
            if len(joueurs_round) % 2 == 1:
                for i in range(len(joueurs_round)-1, -1, -1):
                    cand = joueurs_round[i]
                    if not self.a_eu_bye[cand]:
                        self.a_eu_bye[cand] = True
                        self.scores[cand] += 1.0
                        joueurs_round.pop(i)
                        break
            
            paires = self._trouver_appariements_recursive(joueurs_round)
            if paires is None:
                paires = []
                while len(joueurs_round) >= 2:
                    paires.append((joueurs_round.pop(0), joueurs_round.pop(0)))

            for j1, j2 in paires:
                self.deja_joue[j1].add(j2)
                self.deja_joue[j2].add(j1)
                vainqueur = Match.simuler(j1, j2)
                perdant = j2 if vainqueur == j1 else j1
                Match.update_elo(vainqueur, perdant)
                self.scores[vainqueur] += 1.0

        return sorted(self.participants, key=lambda p: (self.scores[p], p.elo), reverse=True)