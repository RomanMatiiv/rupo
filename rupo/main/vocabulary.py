# -*- coding: utf-8 -*-
# Автор: Гусев Илья
# Описание: Индексы слов для языковой модели.

from typing import Dict, List, Set
import pickle
import os

from rupo.main.markup import Word, Markup
from rupo.files.reader import Reader, FileType


class Vocabulary(object):
    """
    Индексированный словарь.
    """
    def __init__(self, dump_filename: str, markup_path: str=None, is_vocab : bool=False) -> None:
        """
        :param dump_filename: файл, в который сохранется словарь.
        :param markup_path: файл/папка с разметками.
        """
        self.dump_filename = dump_filename
        self.word_to_index = {}  # type: Dict[str, int]
        self.index_to_word = {}
        self.words = []  # type: List[Word]
        self.shorts_set = set()  # type: Set[str]

        if os.path.isfile(self.dump_filename):
            self.load()
        else:
            i = 0
            markups = Reader.read_markups(markup_path, FileType.VOCAB, is_processed=True)
            for i, (markup, index) in enumerate(markups):
                self.add_markup(markup, index)
                if i % 50 == 0:
                    print(i)
            self.save()

    def save(self) -> None:
        """
        Сохранение словаря.
        """
        with open(self.dump_filename, "wb") as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    def load(self):
        """
        Загрузка словаря.
        """
        with open(self.dump_filename, "rb") as f:
            vocab = pickle.load(f)
            self.__dict__.update(vocab.__dict__)

    def add_markup(self, markup: Markup, index : int=-1) -> None:
        """
        Добавление слов из разметки в словарь.

        :param markup: разметка.
        """
        for line in markup.lines:
            for word in line.words:
                self.add_word(word, index)

    def add_word(self, word: Word, index : int=-1) -> bool:
        """
        Добавление слова.

        :param word: слово.
        :return: слово новое или нет.
        """
        short = word.get_short()
        if short not in self.shorts_set:
            self.words.append(word)
            self.shorts_set.add(short)
            self.word_to_index[short] = len(self.words) if index == -1 else index
            self.index_to_word[len(self.words) if index == -1 else index] = word
            return True
        return False

    def get_word_index(self, word: Word) -> int:
        """
        Получить индекс слова.

        :param word: слово (Word).
        :return: индекс.
        """
        short = word.get_short()
        if short in self.word_to_index:
            return self.word_to_index[short]
        raise IndexError("Can't find word: " + word.text)

    def get_word(self, index: int) -> Word:
        """
        Получить слово по индексу.

        :param index: индекс.
        :return: слово.
        """
        return self.index_to_word[index] if index in self.index_to_word else Word(0, 0, '', [])

    def shrink(self, short_words: List[str]) -> None:
        """
        Обрезать словарь по заданным коротким формам слов.

        :param short_words: короткие формы слов.
        """
        new_words = []
        new_shorts_set = set()
        short_words = set(short_words)
        for word in self.words:
            short = word.get_short()
            if short in short_words:
                new_words.append(word)
                new_shorts_set.add(short)
                self.word_to_index[short] = len(new_words)
        self.shorts_set = new_shorts_set
        self.words = new_words

