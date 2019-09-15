from nltk.tag import StanfordPOSTagger
from nltk import word_tokenize

from src.jeeves_bot import Jeeves
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)

if __name__ == '__main__':

    jeeves = Jeeves()
    jeeves.start()