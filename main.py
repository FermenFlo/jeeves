from nltk.tag import StanfordPOSTagger
from nltk import word_tokenize

from src.jeeves import Jeeves
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)

if __name__ == '__main__':

    ner_jar = 'ner/stanford-postagger-2018-10-16/stanford-postagger.jar'
    ner_model = 'ner/stanford-postagger-2018-10-16/models/english-bidirectional-distsim.tagger'

    pos_tagger = StanfordPOSTagger(ner_model, ner_jar, encoding='utf8')

    text = pos_tagger.tag(word_tokenize("What's the airspeed of an unladen swallow ?"))
    print(text)

    jeeves = Jeeves()
    jeeves.start()