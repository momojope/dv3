# -*- coding: utf-8 -*-

from typing import Tuple
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import scipy.stats as sp
import sys

sns.set()


OUTPUT_TEMPLATE = (
    "Valeur-p du Test t initial (invalide):\t\t{initial_ttest_p:.3g}\n"
    "Valeur-p de normalité des données originales:\t\t{initial_weekday_normality_p:.3g}, {initial_weekend_normality_p:.3g}\n"
    "Valeur-p de variance égale des données originales:\t\t{initial_levene_p:.3g}\n"
    "Valeur-p de normalité des données transformées:\t\t{transformed_weekday_normality_p:.3g}, {transformed_weekend_normality_p:.3g}\n"
    "Valeur-p de variance égale des données transformées::\t{transformed_levene_p:.3g}\n"
    "Valeur-p de normalité des données hebdomadaires:\t\t\t{weekly_weekday_normality_p:.3g}, {weekly_weekend_normality_p:.3g}\n"
    "Valeur-p de variance égale des données hebdomadaires:\t\t{weekly_levene_p:.3g}\n"
    "Valeur-p du Test t hebdomadaire:\t\t\t\t{weekly_ttest_p:.3g}\n"
    "Valeur-p du Test U Mann-Whitney:\t\t\t{utest_p:.3g}"
)

def read_data(path: str) -> pd.DataFrame:
    # do not modify
    return pd.read_json(path, lines=True) 


def split_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # do not modify
    wd = df.query("is_weekend==False")
    we = df.query("is_weekend==True")
    return wd, we


def draw_histogram(df: pd.DataFrame, title: str = None) -> Figure:
    # do not modify
    fig, ax = plt.subplots(1, 1, dpi=100)
    ret = sns.histplot(data=df, x='comment_count', hue='is_weekend', ax=ax)
    if title:
        ret.set(title=title)
    return fig


# TODO - Complétez cette méthode
def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """Traiter le DataFrame brut:

        1. Gardez juste le subreddit 'canada'
        2. Gardez juste les années 2012 et 2013
        3. Ajoutez une nouvelle colonne'is_weekend' avec une valeure boolean True/False 
    
    Args:
        df (pd.DataFrame): dataframe à traiter; contient les colonnes
            'date', 'subreddit', 'comment_count' par défaut

    Returns:
        pd.DataFrame: Doit avoir au minimum les colonnes: 'comment_count', 'date', 'is_weekend'
    """
    df = df.copy()  # copy pour que vous ne modifiez pas le dataframe original 

    # TODO: Filtrez sur years, subreddit, et ajoutez une colonne boolean 'is_weekend' 
    df = df[df['subreddit'] == 'canada']
    df = df[df['date'].dt.year.isin([2012, 2013])]
    df['is_weekend'] = df['date'].dt.dayofweek.isin([5, 6])
    return df


# TODO - Complétez cette méthode
def tests(wd: pd.DataFrame, we: pd.DataFrame, verbose: bool = False) -> Tuple[float, float, float, float]:
    """Effectue un test T entre les deux entrées, en vérifiant si la moyenne des deux distributions est
    le même. Vérifie également si les deux ensembles de données d'entrée ont une distribution normale et ont la
    même variance (une exigence pour le test T).

    Référence : https://docs.scipy.org/doc/scipy/reference/stats.html#statistical-tests

    Arguments :
        wd (pd.DataFrame): données en semaine
        we (pd.DataFrame): données du week-end
        verbose (bool): S'il faut afficher les résultats

    Retour:
        Tuple[float, float, float, float] : p_test, p_wd_isnormal, p_we_isnormal, p_vartest
    """
    p_ttest = sp.ttest_ind(wd['comment_count'], we['comment_count']).pvalue
    p_wd_normal = sp.normaltest(wd['comment_count']).pvalue
    p_we_normal = sp.normaltest(we['comment_count']).pvalue
    p_vartest = sp.levene(wd['comment_count'], we['comment_count']).pvalue

    
    # TODO: Obtenez la valeur-p pour le test t

    # TODO: Obtenez la valeur-p pour le test de normalité sur les données en semaine et fin de semaine séparément
    # C'est à dire est-ce que les 2 distributions sont normales

    # TODO: Obtenez la valeur-p pour le test qui vérifie si ces 2 distributions ont la même variance
    # ---------- NE MODIFIEZ PAS LA FONCTION SOUS CETTE LIGNE  ---------- #

    if verbose:
        print(f"p_value:\t{p_ttest.round(5)}")
        print(f"WD normality:\t{p_wd_normal.round(5)}")
        print(f"WE normality:\t{p_we_normal.round(5)}")
        print(f"Variance test:\t{p_vartest.round(5)}")

    return p_ttest, p_wd_normal, p_we_normal, p_vartest


# TODO - Complétez cette méthode
def central_limit_theorem(df: pd.DataFrame) -> pd.DataFrame:
    """Combinez tous les jours de semaine et de week-end de chaque paire année/semaine et prenez la moyenne de leur
    count (non transformé).

    Conseils: Vous pouvez obtenir une "année" et un "numéro de semaine" à partir des deux premières valeurs renvoyées
    par date.isocalendar(). Cette année et ce numéro de semaine vous donneront un identifiant pour la paire (année, semaine).
    Utilisez Pandas pour regrouper par cette valeur et agréger en prenant la moyenne.

    Remarque: l'année renvoyée par isocalendar n'est pas toujours la même que l'année de la date (autour du nouveau
    an). Utilisez l'année de l'isocalendar qui est correcte dans ce cas. Ceci est différent de la
    l'année que vous avez utilisée pour filtrer les événements; n'effectuez aucun filtrage supplémentaire!

    Arguments :
        df (pd.DataFrame) : dataframe nettoyé contenant (au minimum) les colonnes: 'date', 'comment_count', 'is_weekend'

    Retour:
        pd.DataFrame : Doit avoir (au minimum) les colonnes : 'comment_count', 'is_weekend'
    """
    df = df.copy()
    df['year'] = df['date'].dt.isocalendar().year
    df['week'] = df['date'].dt.isocalendar().week

    # Regrouper par année, semaine et si c'est le week-end, puis prendre la moyenne des commentaires
    clt = df.groupby(['year', 'week', 'is_weekend'], as_index=False).agg({'comment_count': 'mean'})

    return clt


# TODO - Complétez cette méthode
def mann_whitney_u_test(wd: pd.DataFrame, we: pd.DataFrame) -> float:
    """Exécutez le test U de Mann-Whitney entre les données du jour de la semaine et celles du week-end.

    Le test U de Mann-Whitney est un test non paramétrique qui peut être utilisé pour décider que des échantillons d'un groupe sont plus grand/plus petits que les observations d'un autre group. Il suppose que les deux groupes ont:
        - Des observations indépendantes
        - Les valeurs sont ordinales (peuvent être triées)

    Rappelons que l'hypothèse alternative pour un test de 2 côtés stipule:
        Supposons que F(u) et G(u) sont les fonctions de distribution cumulées des distributions
        qui ont donnés x et y, respectivement. Alors l'hypothèse alternative est que les distributions
        ne sont pas égaux, c'est-à-dire F(u) ≠ G(u) pour au moins un u.

    Arguments :
        wd (pd.DataFrame): données en semaine
        we (pd.DataFrame): données du week-end

    Retour:
        float : valeur de p du test de Mann-Whitney-U
    """
    # TODO

    return sp.mannwhitneyu(wd['comment_count'], we['comment_count'], alternative="two-sided").pvalue


def main():
    """ 
    Note: rien dans main() va être évalué, le code ici est juste pour aider à diriger le dévelopment de votre code
    """
    path = "./data/reddit-counts.json.gz"
    if len(sys.argv) > 1:
        path = sys.argv[1]

    # load data
    raw_df = read_data(path)

    # preliminary processing
    df = process_data(raw_df)
    wd, we = split_data(df)
    p_ttest, p_wd_normal, p_we_normal, p_vartest = tests(wd, we)

    # fix 1: best transformed tests
    trans = df.copy()

    trans['comment_count'] = np.log1p(trans['comment_count'])  # log(1 + x) pour éviter log(0)  
    # TODO: apply some transformation to the data

    T_wd, T_we = split_data(trans)
    p_T_ttest, p_T_wd_normal, p_T_we_normal, p_T_vartest = tests(T_wd, T_we)

    # fix 2: central limit theorem tests
    clt = central_limit_theorem(df)
    clt_wd, clt_we = split_data(clt)
    p_clt_ttest, p_clt_wd_normal, p_clt_we_normal, p_clt_vartest = tests(clt_wd, clt_we)

    # fix 3: u tests on original data
    p_utest = mann_whitney_u_test(wd, we)


    print(OUTPUT_TEMPLATE.format(
        initial_ttest_p = p_ttest,

        initial_weekday_normality_p = p_wd_normal,
        initial_weekend_normality_p = p_we_normal,
        initial_levene_p = p_vartest,

        transformed_weekday_normality_p = p_T_wd_normal,
        transformed_weekend_normality_p = p_T_we_normal,
        transformed_levene_p = p_T_vartest,

        weekly_weekday_normality_p=p_clt_wd_normal,
        weekly_weekend_normality_p=p_clt_we_normal,
        weekly_levene_p=p_clt_vartest,
        weekly_ttest_p=p_clt_ttest,

        utest_p = p_utest,
    ))

if __name__ == '__main__':
    main()
