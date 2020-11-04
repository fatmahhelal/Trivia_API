import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
import sys
from collections.abc import Callable

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', '123456','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
       
        self.new_question = {
            'question': 'Where Is Fatimah Alhelal from?',
            'answer': 'KSA',
            'difficulty':'1',
            'category': '3'
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass


#test for successful operation and for expected errors.
    
    #test GET requests for all available categories
    def test_get_categories(self):
        #get categories endpoint test function
        res = self.client().get('/categories')
        data = json.loads(res.data)
    
        # check status code and message
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['total_categories'])


    # test GET requests for all available questions
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        # check status code and message
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))


    #test error GET requests for questions page
    def test_404_error_page_questions(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        # check status code and message
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    # test DELETE question using a question ID. 
    def test_delete_question(self):
        res = self.client().delete('questions/50')
        data = json.loads(res.data)
        
        question = Question.query.filter(Question.id == 50).one_or_none()
    
        # check status code and message
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 3)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(question, None)


    # test error DELETE question using a not exite question ID. 
    def test_404_delete_unexist_question(self):
        res = self.client().delete('questions/5000')
        data = json.loads(res.data)
            
        # check status code and message
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    #test Post questions creation endpoint 
    def test_create_question(self):
        res = self.client().post('/questions', json= self.new_question)
        data = json.loads(res.data)
        
        # check status code and message
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['question']))
    

    #test Post questions creation error endpoint 
    def test_422_error_create_question(self):
        res = self.client().post('/questions', json= self.new_question)
        data = json.loads(res.data)
        pass


    #test Post questions search endpoint 
    def test_questions_search(self):
        res = self.client().post('/questions/search', json={'searchTerm': "where"})
        data = json.loads(res.data)

        # check status code and message
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))


    #Test Post questions search error endpoint 
    def test_422_questions_search(self):
        res = self.client().post('/questions/search', json={'searchTerm': "noword"})
        data = json.loads(res.data)
        pass


    #test Get questions by category error endpoint 
    def test_get_questions_categories(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        # check status code and message
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['current_category']), 'nonpp')


    #test Get questions by category error endpoint 
    def test_422_error_questions_categories(self):
        res = self.client().get('/categories/10051/questions')
        data = json.loads(res.data)
        pass


    #test Post play quizz endpoint 
    def test_play_quizz(self):
        res = self.client().post('/quizzes', json={'previous_questions': [],'quiz_category': {"id":"0"} })
        data = json.loads(res.data)
        
        # check status code and message
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


    #test Post play quizz error endpoint 
    def test_422_error_play_quizz(self):
        res = self.client().post('/quizzes', json={'previous_questions': [],'quiz_category': {"id":"7004"} })
        data = json.loads(res.data)
        pass

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()