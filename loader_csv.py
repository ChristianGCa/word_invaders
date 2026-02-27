import csv
import os

def load_words(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError("Arquivo CSV não encontrado.")

    words = []

    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            pt = row["pt-br"]
            len_pt = int(row["len-pt-br"])
            en = row["en"]
            len_en = int(row["len-en"])

            if len(pt) != len_pt:
                raise ValueError(f"Erro tamanho PT-BR: {pt}")

            if len(en) != len_en:
                raise ValueError(f"Erro tamanho EN: {en}")

            words.append({
                "pt": pt,
                "en": en,
                "len_pt": len_pt,
                "len_en": len_en
            })

    return words