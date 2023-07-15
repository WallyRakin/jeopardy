import unittest
from app import app
from flask import session
from boggle import Boggle
from datetime import datetime, timedelta
import json


class boggle_tests(unittest.TestCase):

    def setUp(self):
        self.boggle_game = Boggle()

    def test_read_dict(self):
        self.assertEqual(type(self.boggle_game.read_dict("words.txt")), list)

    def test_make_baord(self):
        board = self.boggle_game.make_board()
        self.assertEqual(len(board), 5)
        for row in board:
            self.assertEqual(type(row), list)
            self.assertEqual(len(row), 5)
            for obj in row:
                self.assertEqual(type(obj), str)
                self.assertEqual(len(obj), 1)
                self.assertIn(obj, [chr(i)
                              for i in range(ord('A'), ord('Z')+1)])

    def test_check_valid_word(self):
        board = [["Y", "Y", "Z", "I", "H"], ["Y", "H", "C", "N", "G"], [
            "G", "V", "S", "S", "M"], ["F", "N", "B", "U", "I"], ["P", "M", "J", "X", "V"]]
        self.assertEqual(self.boggle_game.check_valid_word(board, 'bus'), 'ok')
        self.assertEqual(self.boggle_game.check_valid_word(
            board, 'apple'), 'not-on-board')
        self.assertEqual(self.boggle_game.check_valid_word(
            board, 'yyzih'), 'not-word')
        self.assertEqual(self.boggle_game.check_valid_word(
            board, 'bu'), 'word is too short')

    def test_find_from(self):
        board = [["Y", "Y", "Z", "I", "H"], ["Y", "H", "C", "N", "G"], [
            "G", "V", "S", "S", "M"], ["F", "N", "B", "U", "I"], ["P", "M", "J", "X", "V"]]
        self.assertTrue(self.boggle_game.find_from(
            board, 'ZINC', 0, 2, seen=set()))
        self.assertTrue(self.boggle_game.find_from(
            board, 'BUS', 3, 2, seen=set()))
        self.assertFalse(self.boggle_game.find_from(
            board, 'ZINC', 0, 0, seen=set()))
        self.assertFalse(self.boggle_game.find_from(
            board, 'BUS', 0, 0, seen=set()))

    def test_find(self):
        board = [["Y", "Y", "Z", "I", "H"], ["Y", "H", "C", "N", "G"], [
            "G", "V", "S", "S", "M"], ["F", "N", "B", "U", "I"], ["P", "M", "J", "X", "V"]]
        self.assertTrue(self.boggle_game.find(board, 'BUS'))
        self.assertTrue(self.boggle_game.find(board, 'ZINC'))


class blask_tests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_home(self):
        with self.app.session_transaction() as session:
            session['data'] = '[["Y", "Y", "Z", "I", "H"], ["Y", "H", "C", "N", "G"], ["G", "V", "S", "S", "M"], ["F", "N", "B", "U", "I"], ["P", "M", "J", "X", "V"]]'
            session['end-time'] = str((datetime.now() +
                                       timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S'))
            session['score'] = '0'
            session['found-words'] = '[]'
        response = self.app.get()

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"<title>Home</title>", response.data)

    def test_game_get(self):

        with self.app.session_transaction() as session:
            session['data'] = '[["Y", "Y", "Z", "I", "H"], ["Y", "H", "C", "N", "G"], ["G", "V", "S", "S", "M"], ["F", "N", "B", "U", "I"], ["P", "M", "J", "X", "V"]]'
            end_time = str((datetime.now() +
                            timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S'))
            session['end-time'] = end_time
            session['score'] = '0'
            session['found-words'] = '[]'

        response = self.app.get('/game')
        self.assertEqual({"board": json.loads(
            '[["Y", "Y", "Z", "I", "H"], ["Y", "H", "C", "N", "G"], ["G", "V", "S", "S", "M"], ["F", "N", "B", "U", "I"], ["P", "M", "J", "X", "V"]]'),
            "endTime": end_time,
            "score": '0'},
            json.loads(response.data)
        )

    def test_game_post(self):

        with self.app.session_transaction() as session:
            session['data'] = '[["Y", "Y", "Z", "I", "H"], ["Y", "H", "C", "N", "G"], ["G", "V", "S", "S", "M"], ["F", "N", "B", "U", "I"], ["P", "M", "J", "X", "V"]]'
            session['end-time'] = str((datetime.now() +
                                       timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S'))
            session['score'] = '0'
            session['found-words'] = '[]'

        # Test valid word
        response = self.app.post('/game', json={'word': 'bus'})
        self.assertEqual(b'ok', response.data)

        # Test invalid word
        response = self.app.post('/game', json={'word': 'fnbui'})
        self.assertNotEqual(b'ok', response.data)

        # Test word that is too short
        response = self.app.post('/game', json={'word': 'fn'})
        self.assertNotEqual(b'ok', response.data)

        # Test valid word that doesn't exist
        response = self.app.post('/game', json={'word': 'apple'})
        self.assertNotEqual(b'ok', response.data)

        with self.app.session_transaction() as session:
            session['data'] = '[["Y", "Y", "Z", "I", "H"], ["Y", "H", "C", "N", "G"], ["G", "V", "S", "S", "M"], ["F", "N", "B", "U", "I"], ["P", "M", "J", "X", "V"]]'
            session['end-time'] = str((datetime.now() -
                                       timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S'))  # Set time to the past to simulate a timed-out game
            session['score'] = '100'
            session['found-words'] = json.dumps(['bus'])

            # Test valid word after timed out
        response = self.app.post('/game', json={'word': 'zinc'})
        self.assertEqual(
            b"can't add anymore words, game is already over", response.data)

        with self.app.session_transaction() as session:
            session['data'] = '[["Y", "Y", "Z", "I", "H"], ["Y", "H", "C", "N", "G"], ["G", "V", "S", "S", "M"], ["F", "N", "B", "U", "I"], ["P", "M", "J", "X", "V"]]'
            session['end-time'] = str((datetime.now() +
                                       timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S'))  # Set time to the past to simulate a timed-out game
            session['score'] = '100'
            session['found-words'] = json.dumps(['bus'])

        response = self.app.post('/game', json={'word': 'bus'})
        self.assertEqual(
            b'word has already been selected', response.data)


if __name__ == '__main__':
    unittest.main()
