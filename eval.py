from sklearn.metrics import accuracy_score, precision_score
from abc import ABC, abstractmethod

class Score(ABC):
    @abstractmethod
    def calculate(labels, preds):
        pass

class AccuracyScore(ABC):
    def calculate(labels, preds):
        return accuracy_score(labels, preds)
