import numpy as np

class AttributionPoints:

    @staticmethod
    def lineaire(classement):
        points = {}
        for rang, joueurs in classement.items():
            for j in joueurs:
                points[j] = rang
        return points

    @staticmethod
    def exponentielle(classement):
        points = {}
        for rang, joueurs in classement.items():
            for j in joueurs:
                points[j] = np.exp(rang)
        return points

    @staticmethod
    def logarithmique(classement):
        points = {}
        for rang, joueurs in classement.items():
            for j in joueurs:
                points[j] = np.log(rang)
        return points
