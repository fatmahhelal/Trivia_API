import os
import sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.sql.expression import func
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

#defined a paginating questions function
def paginate_question(request, selection):
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_question = questions[start:end]
    return current_question


# create and configure the app
def create_app(test_config=None):
  app = Flask(__name__)
  setup_db(app)
    # set up CORS, allowing all origins
  CORS(app, resources={'/': {'origins': '*'}})  


  # CORS Headers 
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
      return response


#endpoint to handle GET requests for all available categories
  @app.route('/categories')
  def get_categories():

    categories = Category.query.order_by(Category.id).all()
     # abort 404 if no categories available
    if len(categories) == 0:
        abort(404)
    
    # return success response
    return jsonify({
                'success': True,
                'categories': {category.id: category.type for category in categories},
                'total_categories': len(categories)
            })


#endpoint to handle GET requests for all available questions
  @app.route('/questions')
  def get_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_question(request, selection)
    categories = Category.query.all()

    # abort 404 if no questions available
    if len(current_questions) == 0:
              abort(404)

    # return success response
    return jsonify({
              'success': True,
              'questions': current_questions,
              'total_questions': len(selection),
              'current_category': list(set([question['category'] for question in current_questions])),
              'categories': {category.id: category.type for category in categories},
          })


#endpoint to DELETE question using a question ID. 
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
      question = Question.query.filter(Question.id == question_id).one_or_none()
      #abort 404 if the question not found
      if question is None:
         abort(404)

      # delete the question
      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_question(request, selection)

       # return success response
      return jsonify({
         'success': True,
         'deleted': question_id,
         'questions': current_questions,
         'total_questions': len(Question.query.all())
         })


#endpoint to POST a new question, 
  @app.route("/questions", methods=['POST'])
  def create_question():
        body = request.get_json()
     
        #abort 422 if the requst is bad 
        if not ('question' in body and 'answer' in body and 'difficulty' in body and 'category' in body):
            abort(400)
        #get the new question's informatin
        new_question = body.get('question')
        new_answer = body.get('answer')
        new_difficulty = body.get('difficulty')
        new_category = body.get('category')

        #insert the questions and paginate
        try:
            question = Question(question=new_question, answer=new_answer,difficulty=new_difficulty, category=new_category)
            question.insert()
            selection = Question.query.order_by(Question.id).all()
            current_books = paginate_question(request, selection)

            # return success response
            return jsonify({
                'success': True,
                'created': question.id,
                'question': current_books, 
                'total_questions': len(Question.query.all())
            })

        #abort 422 if the request is unprocessable     
        except:
            abort(422)


#POST endpoint to get questions based on a search term. 
  @app.route('/questions/search', methods=['POST'])
  def questions_search():
    body = request.get_json()
    question = body.get('searchTerm')
        
    #filter the database by search term & paginate the results
    try:
     selection = Question.query.filter(Question.question.ilike('%{}%'.format(question))).all()
     current_questions = paginate_question(request, selection)
     
     #abort 404 if the question not found
     if len(current_questions) == 0:
        abort(404)

      # return success response
     return jsonify({
        "success": True,
        "questions": current_questions,
        "total_questions": len(selection),
        "current_category": list(set([question['category'] for question in current_questions])), 
        })
    #abort 400 if the request is bad 
    except:
     abort(400)


#GET endpoint to get questions based on category. 
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_categories(category_id):
    
    #query a available category filter by category_id 
    current_category = Category.query.filter(Category.id == category_id).one_or_none()
    
    #abort 404 if the category not found
    if current_category is None:
      abort(404)
        
    #query a available questions & paginate the results
    selection = Question.query.filter(Question.category == category_id).all()
    current_questions = paginate_question(request, selection)
        
    #abort 404 if the questions not found
    if len(current_questions) == 0:
      abort(404)
        
    # return success response
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(current_questions),
      'current_category': current_category.format()
        })

 
  #POST endpoint to get questions to play the quiz. 
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    body = request.get_json()
    if not ('previous_questions' in body and 'quiz_category' in body):
      abort(404)
      
    try:
      previous_question = body.get('previous_questions')
      category = body.get('quiz_category')
      category_id = int(category['id'])
      previous_questions_len = len(previous_question)
                
       #First question in quiz & All {id=0} or a specific category selected
      if previous_questions_len == 0:
        if category_id == 0:
          question = Question.query.order_by(func.random()).first()
        else:
          question = Question.query.filter(Question.category == category['id']).order_by(func.random()).first()

       #Not first question in quiz & All {id=0} or a specific category selected
      else:
        if category_id == 0:
           question = Question.query.filter(~Question.id.in_(previous_question)).order_by(func.random()).first()
        else:
            question = Question.query.filter(Question.category == category_id, Question.id.in_(previous_question))\
                        .order_by(func.random()).first()

      # return success response
      return jsonify({
        'success': True,
        'question': question.format()
            })

    except Exception:
      abort(422)


 #error handlers for all expected errors 400, 404 and 422. 
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
       "success": False, 
       "error": 404,
       "message": "resource not found"
        }), 404

  @app.errorhandler(422)
  def unprocessable(error):
        return jsonify({
            "success": False, 
            "error": 422,
            "message": "unprocessable"
        }), 422

  @app.errorhandler(400)
  def bad_request(error):
        return jsonify({
            "success": False, 
            "error": 400,
            "message": "bad request"
        }), 400
  
  
  return app



    