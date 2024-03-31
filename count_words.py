def count_words(sentence):
    words = sentence.split()  # Splitting the sentence into words based on spaces
    return len(words)  # Returning the count of words

# Your given sentence
sentence = "Гаррі Поттер (англ. Harry Potter) — серія з семи фантастичних романів англійської письменниці..."

# Counting the words
word_count = count_words(sentence)
print(f"Number of words in the sentence: {word_count}")