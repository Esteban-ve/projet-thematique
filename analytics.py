# analytics.py
import numpy as np
import pandas as pd


def snapshots_to_df(snapshots):
    """
    snapshots: liste de listes de dicts
    -> DataFrame avec une ligne par joueur et par ronde.
    """
    rows = [row for snap in snapshots for row in snap]
    return pd.DataFrame(rows)


def rank_round(df_round):
    """
    Classe une ronde :
    - tri par score décroissant puis Elo décroissant
    - ajoute une colonne 'rang' (1 = meilleur).
    """
    df = df_round.sort_values(["score", "elo"], ascending=[False, False]).copy()
    df["rang"] = range(1, len(df) + 1)
    return df


def spearman_corr(x, y):
    """
    Corrélation de Spearman entre x et y :
    Spearman(x, y) = Pearson(rang(x), rang(y)).
    """
    rx = pd.Series(x).rank(method="average")
    ry = pd.Series(y).rank(method="average")

    if rx.std() == 0 or ry.std() == 0:
        return 0.0

    return float(np.corrcoef(rx, ry)[0, 1])


def metrics(df_ranked):
    """
    df_ranked doit contenir:
        - 'niveau_reel' : force vraie (plus grand = plus fort)
        - 'rang'        : rang final (1 = meilleur)

    Retourne:
        - spearman : corr(niveau_reel, -rang)
        - mae_rank : erreur moyenne de rang
                     MAE = (1/N) * Σ |rang_observé - rang_vrai|
    """
    # plus le niveau réel est grand, plus le rang devrait être petit -> on corrèle avec -rang
    spearman = spearman_corr(df_ranked["niveau_reel"], -df_ranked["rang"])

    df_ranked = df_ranked.copy()
    # rang_vrai = rang si on classait uniquement par niveau_reel décroissant
    df_ranked["rang_vrai"] = df_ranked["niveau_reel"].rank(
        ascending=False,  # plus fort -> rang 1
        method="average"
    )

    mae_rank = float((df_ranked["rang"] - df_ranked["rang_vrai"]).abs().mean())

    return {"spearman": spearman, "mae_rank": mae_rank}


def topk_accuracy(df_ranked, k=3):
    """
    top-k accuracy:
        = | top_k_vrai ∩ top_k_final | / k

    - top_k_vrai : k plus gros 'niveau_reel'
    - top_k_final : k plus petits 'rang'
    """
    topk_true = set(
        df_ranked.sort_values("niveau_reel", ascending=False).head(k)["nom"]
    )
    topk_final = set(
        df_ranked.sort_values("rang").head(k)["nom"]
    )

    return len(topk_true & topk_final) / k
