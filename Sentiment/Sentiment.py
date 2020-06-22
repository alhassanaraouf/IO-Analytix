# import libraries
import hashlib
import orgparse as org
import math
import string
import sqlite3
import os


class Sentiment:
    def __init__(self):
        "docstring"
        pass

    C_INCR = 0.733
    N_SCALAR = -0.74

    B_INCR = 0.293
    B_DECR = -0.293

    BOOSTER_DICT = {
        "absolutely": B_INCR,
        "amazingly": B_INCR,
        "awfully": B_INCR,
        "completely": B_INCR,
        "considerable": B_INCR,
        "considerably": B_INCR,
        "decidedly": B_INCR,
        "deeply": B_INCR,
        "effing": B_INCR,
        "enormous": B_INCR,
        "enormously": B_INCR,
        "entirely": B_INCR,
        "especially": B_INCR,
        "exceptional": B_INCR,
        "exceptionally": B_INCR,
        "extreme": B_INCR,
        "extremely": B_INCR,
        "fabulously": B_INCR,
        "flipping": B_INCR,
        "flippin": B_INCR,
        "frackin": B_INCR,
        "fracking": B_INCR,
        "fricking": B_INCR,
        "frickin": B_INCR,
        "frigging": B_INCR,
        "friggin": B_INCR,
        "fully": B_INCR,
        "fuckin": B_INCR,
        "fucking": B_INCR,
        "fuggin": B_INCR,
        "fugging": B_INCR,
        "greatly": B_INCR,
        "hella": B_INCR,
        "highly": B_INCR,
        "hugely": B_INCR,
        "incredible": B_INCR,
        "incredibly": B_INCR,
        "intensely": B_INCR,
        "major": B_INCR,
        "majorly": B_INCR,
        "more": B_INCR,
        "most": B_INCR,
        "particularly": B_INCR,
        "purely": B_INCR,
        "quite": B_INCR,
        "really": B_INCR,
        "remarkably": B_INCR,
        "so": B_INCR,
        "substantially": B_INCR,
        "thoroughly": B_INCR,
        "total": B_INCR,
        "totally": B_INCR,
        "tremendous": B_INCR,
        "tremendously": B_INCR,
        "uber": B_INCR,
        "unbelievably": B_INCR,
        "unusually": B_INCR,
        "utter": B_INCR,
        "utterly": B_INCR,
        "very": B_INCR,
        "almost": B_DECR,
        "barely": B_DECR,
        "hardly": B_DECR,
        "just enough": B_DECR,
        "kind of": B_DECR,
        "kinda": B_DECR,
        "kindof": B_DECR,
        "kind-of": B_DECR,
        "less": B_DECR,
        "little": B_DECR,
        "marginal": B_DECR,
        "marginally": B_DECR,
        "occasional": B_DECR,
        "occasionally": B_DECR,
        "partly": B_DECR,
        "scarce": B_DECR,
        "scarcely": B_DECR,
        "slight": B_DECR,
        "slightly": B_DECR,
        "somewhat": B_DECR,
        "sort of": B_DECR,
        "sorta": B_DECR,
        "sortof": B_DECR,
        "sort-of": B_DECR,
    }

    def make_Negations_list(self):
        """
        Convert Negations lexicon file to a list
        """
        file = open("dict/Negations_Words.txt")
        Negations = file.read()
        file.close()
        Negations_list = []
        for line in Negations.split("\n"):
            word = line.strip().split("\t")[0]
            Negations_list.append(word)
        return Negations_list

    def make_lexicon_dict(self):
        """
        Convert words lexicon file to a dictionary
        """
        file = open("dict/words_lexicon.txt")
        words = file.read()
        file.close()

        lexicon_dict = {}
        for line in words.split("\n"):
            if not line:
                continue
            (words, score) = line.strip().split("\t")[0:2]
            lexicon_dict[words] = float(score)
        return lexicon_dict

    def make_emoji_dict(self):
        """
        Convert emoji lexicon file to a dictionary
        """
        file = open("dict/emoji_utf8_lexicon.txt", encoding="utf-8")
        emoji = file.read()
        file.close()

        emoji_dict = {}
        for line in emoji.split("\n"):
            (emoji, description) = line.strip().split("\t")[0:2]
            emoji_dict[emoji] = description
        return emoji_dict

    def negated(self, input_words, include_nt=True):
        """
        Determine if input contains negation words
        """
        input_words = [str(w).lower() for w in input_words]
        neg_words = []
        neg_words.extend(self.make_Negations_list())
        for word in neg_words:
            if word in input_words:
                return True
        if include_nt:
            for word in input_words:
                if "n't" in word:
                    return True
        """if "least" in input_words:
            i = input_words.index("least")
            if i > 0 and input_words[i - 1] != "at":
                return True"""
        return False

    def normalize(self, score, alpha=15):
        """
        Normalize the score to be between -1 and 1 using an alpha that
        approximates the max expected value
        """
        norm_score = score / math.sqrt((score * score) + alpha)
        if norm_score < -1.0:
            return -1.0
        elif norm_score > 1.0:
            return 1.0
        else:
            return norm_score

    def _strip_punc_if_word(self, token):
        """
        Removes all trailing and leading punctuation
        If the resulting string has two or fewer characters,
        then it was likely an emoticon, so return original string
        (ie ":)" stripped would be "", so just return ":)"
        """
        stripped = token.strip(string.punctuation)
        if len(stripped) <= 2:
            return token
        return stripped

    def words_and_emoticons(self, text):
        text_list = []
        for word in text.split():
            text_list.append(self._strip_punc_if_word(word))
        return text_list

    def is_cap_diff(self, words):
        is_different = False
        allcap_words = 0
        for word in words.split():
            if word.isupper():
                allcap_words += 1
        cap_differential = len(words.split()) - allcap_words
        if 0 < cap_differential < len(words.split()):
            is_different = True
        return is_different

    def scalar_Booster_dict(self, word, valence, is_all_cap):
        """
        Check if the preceding words increase, decrease, or negate/nullify the
        valence
        """
        scalar = 0.0
        word_lower = word.lower()
        if word_lower in self.BOOSTER_DICT:
            scalar = self.BOOSTER_DICT[word_lower]
            if valence < 0:
                scalar *= -1
            # check if booster/dampener word is in ALLCAPS (while others aren't)
            if word.isupper() and self.is_cap_diff:
                if valence > 0:
                    scalar += self.C_INCR
                else:
                    scalar -= self.C_INCR
        return scalar

    def polarity_scores(self, tweet):
        # convert emojis to their textual descriptions
        text_no_emoji = ""
        prev_space = True
        emoji_dict = {}
        emoji_dict = self.make_emoji_dict()

        for chr in tweet:
            if chr in emoji_dict:
                # get the textual description
                description = emoji_dict[chr]
                if not prev_space:
                    text_no_emoji += " "
                text_no_emoji += description
                prev_space = False
            else:
                text_no_emoji += chr
                prev_space = chr == " "
        text = text_no_emoji.strip()
        words_emoticons = self.words_and_emoticons(text)

        sentiments = []
        Booster_dict = self.BOOSTER_DICT
        for i, item in enumerate(words_emoticons):
            valence = 0
            # check for vader_lexicon words that may be used as modifiers or negations
            if item.lower() in Booster_dict:
                sentiments.append(valence)
                continue
            if (
                i < len(words_emoticons) - 1
                and item.lower() == "kind"
                and words_emoticons[i + 1].lower() == "of"
            ):
                sentiments.append(valence)
                continue
            sentiments = self.sentiment_valence(valence, item, i, sentiments, text)
        sentiments = self._but_check(words_emoticons, sentiments)
        valence_dict = self.score_valence(sentiments, text)
        return valence_dict

    def sentiment_valence(self, valence, item, i, sentiments, text):
        is_all_cap = self.is_cap_diff(text)
        words_emoticons = self.words_and_emoticons(text)
        item_lowercase = item.lower()
        lexicon_dict = self.make_lexicon_dict()

        if item_lowercase in lexicon_dict:
            valence = lexicon_dict[item_lowercase]

            # check for "no" as negation for an adjacent lexicon item vs "no" as its own stand-alone lexicon item
            if (
                item_lowercase == "no"
                and words_emoticons[i + 1].lower() in lexicon_dict
            ):
                # don't use valence of "no" as a lexicon item. Instead set it's valence to 0.0 and negate the next item
                valence = 0.0
            if (
                (i > 0 and words_emoticons[i - 1].lower() == "no")
                or (i > 1 and words_emoticons[i - 2].lower() == "no")
                or (
                    i > 2
                    and words_emoticons[i - 3].lower() == "no"
                    and words_emoticons[i - 1].lower() in ["or", "nor"]
                )
            ):
                valence = lexicon_dict[item_lowercase] * self.N_SCALAR
            # check if sentiment laden word is in ALL CAPS (while others aren't)
            if item.isupper() and is_all_cap:
                if valence > 0:
                    valence += self.C_INCR
                else:
                    valence -= self.C_INCR

            for start_i in range(0, 3):

                if (
                    i > start_i
                    and words_emoticons[i - (start_i + 1)].lower() not in lexicon_dict
                ):
                    s = self.scalar_Booster_dict(
                        words_emoticons[i - (start_i + 1)], valence, is_all_cap
                    )
                    if start_i == 1 and s != 0:
                        s = s * 0.95
                    if start_i == 2 and s != 0:
                        s = s * 0.9
                    valence = valence + s
                    valence = self._negation_check(valence, words_emoticons, start_i, i)

        sentiments.append(valence)
        return sentiments

    def _negation_check(self, valence, words_and_emoticons, start_i, i):
        words_and_emoticons_lower = [str(w).lower() for w in words_and_emoticons]
        if start_i == 0:
            # 1 word preceding lexicon word (w/o stopwords)
            if self.negated([words_and_emoticons_lower[i - (start_i + 1)]]):
                valence = valence * self.N_SCALAR
        if start_i == 1:
            if words_and_emoticons_lower[i - 2] == "never" and (
                words_and_emoticons_lower[i - 1] == "so"
                or words_and_emoticons_lower[i - 1] == "this"
            ):
                valence = valence * 1.25
            elif (
                words_and_emoticons_lower[i - 2] == "without"
                and words_and_emoticons_lower[i - 1] == "doubt"
            ):
                valence = valence
            # 2 words preceding the lexicon word position
            elif self.negated([words_and_emoticons_lower[i - (start_i + 1)]]):
                valence = valence * self.N_SCALAR
        if start_i == 2:
            if (
                words_and_emoticons_lower[i - 3] == "never"
                and (
                    words_and_emoticons_lower[i - 2] == "so"
                    or words_and_emoticons_lower[i - 2] == "this"
                )
                or (
                    words_and_emoticons_lower[i - 1] == "so"
                    or words_and_emoticons_lower[i - 1] == "this"
                )
            ):
                valence = valence * 1.25
            elif words_and_emoticons_lower[i - 3] == "without" and (
                words_and_emoticons_lower[i - 2] == "doubt"
                or words_and_emoticons_lower[i - 1] == "doubt"
            ):
                valence = valence
            # 3 words preceding the lexicon word position
            elif self.negated([words_and_emoticons_lower[i - (start_i + 1)]]):
                valence = valence * self.N_SCALAR
        return valence

    def _but_check(self, words_and_emoticons, sentiments):
        # check for modification in sentiment due to contrastive conjunction 'but'
        words_and_emoticons_lower = [str(w).lower() for w in words_and_emoticons]
        if "but" in words_and_emoticons_lower:
            bi = words_and_emoticons_lower.index("but")
            for sentiment in sentiments:
                si = sentiments.index(sentiment)
                if si < bi:
                    sentiments.pop(si)
                    sentiments.insert(si, sentiment * 0.5)
                elif si > bi:
                    sentiments.pop(si)
                    sentiments.insert(si, sentiment * 1.5)
        return sentiments

    def _punctuation_emphasis(self, text):
        # add emphasis from exclamation points and question marks
        ep_amplifier = self._amplify_ep(text)
        qm_amplifier = self._amplify_qm(text)
        punct_emph_amplifier = ep_amplifier + qm_amplifier
        return punct_emph_amplifier

    def _amplify_ep(self, text):
        # check for added emphasis resulting from exclamation points (up to 4 of them)
        ep_count = text.count("!")
        if ep_count > 4:
            ep_count = 4
        # (empirically derived mean sentiment intensity rating increase for
        # exclamation points)
        ep_amplifier = ep_count * 0.292
        return ep_amplifier

    def _amplify_qm(self, text):
        # check for added emphasis resulting from question marks (2 or 3+)
        qm_count = text.count("?")
        qm_amplifier = 0
        if qm_count > 1:
            if qm_count <= 3:
                # (empirically derived mean sentiment intensity rating increase for
                # question marks)
                qm_amplifier = qm_count * 0.18
            else:
                qm_amplifier = 0.96
        return qm_amplifier

    def score_valence(self, sentiments, text):
        if sentiments:
            sum_score = float(sum(sentiments))
            # compute and add emphasis from punctuation in text
            punct_emph_amplifier = self._punctuation_emphasis(text)

            if sum_score > 0:
                sum_score += punct_emph_amplifier
            elif sum_score < 0:
                sum_score -= punct_emph_amplifier

            compound = self.normalize(sum_score)

        else:
            compound = 0.0

        sentiment_dict = {"compound": round(compound, 4)}
        return sentiment_dict

    def ListScore(self, list):
        result = []
        for x in list:
            result.append(self.polarity_scores(x))
        return result


class Aspects:
    def __init__(self):
        "docstring"
        pass

    def uploadfile(self):
        if os.path.exists("dict/bagofwords.db"):
            os.remove("dict/bagofwords.db")
        client = sqlite3.connect("dict/bagofwords.db")
        db = client.cursor()
        db.execute("""CREATE TABLE words (id text, keyword text, parent text)""")
        data = org.load("dict/bagofwords.org")
        for x in data[1:]:
            temp = {}
            id = bytes(x.heading.lower(), "utf-8")
            id = hashlib.md5(id).hexdigest()
            temp["_id"] = id
            temp["keyword"] = x.heading.lower()
            if x.parent is data:
                temp["parent"] = ""
            else:
                parent = bytes(x.parent.heading.lower(), "utf-8")
                parent = hashlib.md5(parent).hexdigest()
                temp["parent"] = parent
            db.execute(
                "INSERT INTO words VALUES (?,?,?)",
                (temp["_id"], temp["keyword"], temp["parent"]),
            )
        client.commit()
        client.close()

    def getRelated(self, keyword):
        client = sqlite3.connect("dict/bagofwords.db")
        db = client.cursor()
        keyword = keyword.lower()
        keys = []
        keys.append(keyword)
        h = bytes(keyword, "utf-8")
        h = hashlib.md5(h).hexdigest()
        temp = db.execute("SELECT * FROM words WHERE id=?", (h,)).fetchone()
        if temp is None:
            return
        while temp[2] != "":
            temp = db.execute("SELECT * FROM words WHERE id=?", (temp[2],))
            temp = temp.fetchone()
            keys.append(temp[1])
        return keys
