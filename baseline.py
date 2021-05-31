# -*- coding: utf-8 -*-
from neural_morph_segm import load_cls
from sklearn.metrics import f1_score
import sys
import numpy as np

from root_alternation import find_possible_root_alternations

model = None


def init(path):
    global model
    model = load_cls(path)


def getRoots(words):
    ans = []
    for word, (labels, probs) in zip(words, model._predict_probs(words)):
        morphemes, morpheme_probs, morpheme_types = model.labels_to_morphemes(
            word, labels, probs, return_probs=True, return_types=True)

        ans.append([(morphem, prob) for morphem, prob, morhem_type in zip(
            morphemes, morpheme_probs, morpheme_types) if morhem_type == 'ROOT'])

    return ans


def getBestRoot(res):
    return max(res, key=lambda x: x[1])


def getSubstring(str1, str2):
    from difflib import SequenceMatcher
    match = SequenceMatcher(None, str1, str2).find_longest_match(
        0, len(str1), 0, len(str2))
    return str1[match.a: match.a + match.size]


def getInput(word1, word2):
    word1, word2 = word1.lower(), word2.lower()
    ans = getRoots([word1, word2])

    roots = [(a1[0], a2[0]) for a1 in ans[0] for a2 in ans[1]]

    res = []

    for r in roots:
        substr = getSubstring(*r)
        if len(r) == 1:
            print(roots, word1, word2)
            continue
        if not substr:
            res.append({
                "prefix_1": r[0],
                "postfix_1": "",
                "prefix_2": r[1],
                "postfix_2": "",
                "root_1": r[0],
                "root_2": r[1],
                "substr_len": len(substr)
            })
            continue
        roots_splited = [rot.split(substr) for rot in r]
        res.append({
            "prefix_1": roots_splited[0][0],
            "postfix_1": roots_splited[0][1],
            "prefix_2": roots_splited[1][0],
            "postfix_2": roots_splited[1][1],
            "root_1": r[0],
            "root_2": r[1],
            "substr_len": len(substr)
        })
    return res


res = None

eng_titles = {
    "prefix_1": 3,
    "prefix_2": 4,
    "postfix_1": 5,
    "postfix_2": 6,
    "substr_len": 7
}

for_insert = []


def parseRow(row):
    a = getInput(row[0], row[1])
    if row[-1] == 1 and len(a) > 1:
        row[-1] = 2
    for key in a[0]:
        row[eng_titles[key]] = a[0][key]

    for idx, _ in enumerate(a[1:]):
        a[idx]['Корень_x'] = row[0]
        a[idx]['Корень_y'] = row[1]
        a[idx]['key'] = row[-1]

    for_insert.extend(a[1:])
    return row


# def prepaire_root(row):
#     root_split = row[1].split('_')[0].split('(')
#     base_root = root_split[0]
#     if len(root_split) > 1:
#         end_root = root_split[1][:-1]
#         other_root = f'{base_root[:-len(end_root)]}{end_root}'
#         if other_root in row[0]:
#             return (row[0], other_root)
#     return (row[0], base_root)
def prepaire_root(row):
    # print(row)
    root_split = row['root'].split()
    return generate_bitmask_for_list(row['word'], root_split)


def generate_bitmask(word: str, root: str):
    bitmask = [0] * len(word)
    start_idx = word.find(root)
    for i in range(start_idx, start_idx + len(root)):
        bitmask[i] = 1
    return bitmask


def generate_bitmask_for_list(word: str, roots: list):
    bitmask = [0] * len(word)
    for r in roots:
        start_idx = word.find(r)
        for i in range(start_idx, start_idx + len(r)):
            bitmask[i] = 1
    return bitmask


def f1_for_row(row):
    return f1_score(row[1], row[2])


def get_only_root(pairs):
    return [p[0] for p in pairs]


def getEvristicCognate(word1, word2):
    mix_roots = {"гар": "гор", "клан": "клон", "твар": "твор", "зар": "зор", "плав": "плов", "кас": "кос", "мак": "мок",
                 "равн": "ровн", "раст": "ращ", "ращ": "рос", "рос": "раст", "скак": "скоч", "лаг": "лож",
                 "бер": "бир", "дер": "дир", "мер": "мир", "пер": "пир", "тер": "тир", "жег": "жиг", "блест": "блист",
                 "стел": "стил", "чет": "чит"}
    root1, root2 = getRoots([word1, word2])
    print(root1, root2)
    root1 = get_only_root(root1)
    root2 = get_only_root(root2)
    # TODO: Blyat Danix
    root1 = map(lambda x: x.replace("ё", "е"), root1)
    root2 = map(lambda x: x.replace("ё", "е"), root2)
    root1_mix = []
    for r in root1:
        root1_mix.extend(find_possible_root_alternations(r))
        if r in mix_roots:
            root1_mix.append(mix_roots[r])
    root2_mix = []
    for r in root2:
        root2_mix.extend(find_possible_root_alternations(r))
        if r in mix_roots:
            root1_mix.append(mix_roots[r])

    return bool(set(root1_mix).intersection(root2_mix))


if __name__ == "__main__":
    model = load_cls("models/morphemes-3-5-3-memo_dima.json")

    print(getEvristicCognate('летчик', 'самолет'))
    # import pandas as pd

    # data2 = pd.read_csv("data/test_230_words_ds_common_words_utf_8.csv")

    # res = getRoots(data2['word'])
    # print(len(res), len(data2['word']))

    # roots = [get_only_root(r) for r in res]

    # bitmasks = [generate_bitmask_for_list(word, roots=root_) for root_, word in zip(roots, data2['word'])]
    # # roots = [getBestRoot(r)[0] for r in res]
    # # roots = data2['word'].apply(find_root)

    # data2[1] = data2.apply(prepaire_root, axis=1)
    # data2[2] = bitmasks
    # data2.to_csv('tmp.csv', index=None)
    # res = data2.apply(f1_for_row, axis=1)
    # print(res.mean(axis=0))

    # print(data[10:30])
    # y_res = data[1]
    # print(f1_score(data[1], roots, average='weighted'))
    # print(f1_score(data[1], roots, average='micro'))
    # print(f1_score(data[1], roots, average='macro'))
    # data2_tmp = pd.read_csv("data/ds_common_words_utf_8.csv")
    # data2['key'] = 0
    # data2_tmp['key'] = 0

    # res = data2.merge(data2, on='key',  how='outer').drop("key", 1)
    # res['Y'] = res['Корень_x'] == res['Корень_y']
    # res = res.drop('Корень_x', 1).drop('Корень_y', 1)
    # res['Префикс_1'] = ""
    # res['Префикс_2'] = ""
    # res['Постфикс_1'] = ""
    # res['Постфикс_2'] = ""
    # res['Длина подстроки'] = 0
    # res = res.apply(parseRow, axis=1, raw=True)
    # res.to_csv("data/res.ou t")
    # words = input("Введите два слова: ").split()

    # words_list = list(map(str.strip, words))
    # print(getRoots(words_list))
    # print(getInput(*words_list))
