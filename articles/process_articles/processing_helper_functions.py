import re
import jieba 

def remove_punctuation(text):
    """Remove Chinese punctuation from a text"""
    try:
        return re.sub('[，。：；‘“’”！？（） 【】「」/、｜《》]', "", text)
    except:
        return ""

def parse_chinese(text):
    '''Breaks clean (no punct.) Chinese text into words using jieba'''

    seg_text = jieba.cut(text)
    seg_list = [word for word in seg_text]

    return " ".join(seg_list)
