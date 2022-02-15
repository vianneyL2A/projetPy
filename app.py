
from datetime import date, datetime
import json
import os
import string
from tkinter.messagebox import NO
from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import true
load_dotenv()


app = Flask(__name__)

motdepasse = os.getenv(quote_plus('password'))

#connexion db
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:{}@localhost:5432/python_projet".format(motdepasse)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#instance
db = SQLAlchemy(app)

#Création des classes

class Livre(db.Model):
    __tablename__ = 'livres'
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True) 
    titre = db.Column(db.String(50), nullable=False)
    date_publication = db.Column(db.Date, nullable=False)
    auteur = db.Column(db.String(100), nullable=False)
    editeur = db.Column(db.String(100), nullable=False)
    categorie = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    def __init__(self, isbn, titre, date_publication, auteur, editeur, categorie):
        self.isbn = isbn
        self.titre = titre
        self.date_publication = date_publication
        self.auteur = auteur
        self.editeur = editeur
        self.categorie = categorie
        
    def insert(self):
        db.session.add(self)
        db.session.commit()
        
    def update(self):
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    def format(self):
        return {
            'id' : self.id,
            'isbn' : self.isbn,
            'titre' : self.titre,
            'date de publication' : self.date_publication,
            'Nom de l\'auteur' : self.auteur,
            'Nom de l\'éditeur': self.editeur,
            'Catégorie': self.categorie
        }
    
class Categorie(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    libelle_categorie = db.Column(db.String(100), nullable=False)
    categorie = db.relationship('Livre', backref='categories')
    
    def __init__(self, libelle):
        self.libelle_categorie = libelle
        
    def insert(self):
        db.session.add(self)
        db.session.commit()
        
    def update(self):
        db.session.commit()
    
    def delete(self) :
        db.session.delete(self)
        db.session.commit()
        
    def format(self) :
        return {
            'id' : self.id,
            'Libellé'  : self.libelle_categorie
        }
db.create_all() 

@app.route('/livres', methods=['GET'])
def getAllBooks():
    livres = Livre.query.all()
    livre_formated = [livre.format() for livre in livres]
    return jsonify({
        'Success' : True,
        'livres'  : livre_formated   
    })
    
@app.route('/livres/<int:id>', methods=['GET'])
def get_one_book(id):
    selected_book = Livre.query.get(id)
    if selected_book is None :
        abort(404)
    else :
        return jsonify({
            'success'       : True,
            'selected_id'   : selected_book.id,
            'selected_book' : selected_book.format()
        })
        
@app.route('/livres', methods=['POST'])
def add_book():
        body=request.get_json()
        Isbn = body.get('isbn', None)
        Title = body.get('titre', None)
        p = body.get("date de publication").split("-")
        Date = datetime(int(p[0]), int(p[1]), int(p[2])).date()
        Author = body.get('auteur', None)
        Editor = body.get('editeur', None)
        Category = body.get('categorie', None)
        livre = Livre(isbn=Isbn, titre=Title, date_publication= Date, auteur= Author, editeur=Editor, categorie= Category)
        livre.insert()
        livres = Livre.query.all()
        livre_formated = [i.format() for i in livres]
        return jsonify({
                    'success'   : True,
                    'created_book'  : livre.format(),
                    'Total'         : livre.query.count(),
                    'livres'        : livre_formated
            })

    
@app.route('/categories/<int:id>/livres', methods=['GET'])
def get_books_per_category(id):
        livre = Livre.query.filter(Livre.categorie == id)
        catg = Categorie.query.get(id)
        found = 0
        for i in Livre.query.all():
            if i.categorie == id:
                found = 1
                break
        if catg is None or found == 0:
            abort(404)
        else:
            selected_books = [selected_book.format() for selected_book in livre]
            return jsonify({
                'success'        : True,
                'selected_books' : selected_books
            })

        
@app.route('/categories', methods=['GET'])
def getAllCategories():
    Categories =  Categorie.query.all()
    Cat = [i.format() for i in Categories]
    return jsonify({
        'Success'  : True,
        'categories' : Cat,
        'Total'      :  Categorie.query.count()
    })     

@app.route('/categories/<int:id>', methods=['GET'])
def get_one_category(id):
    categorie = Categorie.query.get(id)
    if categorie is None:
        abort(404)
    else:
        return jsonify({
                'selected_id' : categorie.id,
                'success' : True,
                'Categories' : categorie.format()
        })
@app.route('/livres/<int:id>', methods=['DELETE'])
def drop_book(id):
    l = Livre.query.get(id)
    if l is None:
        abort(404)
    else:
        l.delete()
        livre = Livre.query.all()
        formated_livre = [i.format() for i in livre]
        return jsonify({
            'deleted_id'   : l.id,
            'Total'  : Livre.query.count(),
            'Livres' : formated_livre
        })
@app.route('/categories/<int:id>', methods=['DELETE'])
def drop_categorie(id):
    delete_categorie = Categorie.query.get(id)
    livre = Livre.query.filter(Livre.categorie == id)
    if delete_categorie is None :
        abort(404)
    elif livre is not None:
        return jsonify({
            'Message'  : 'echec de la suppression de la categorie'
        })
    else :
        for i in livre:
            drop_book(i.categorie)
        drop_categorie.delete()
        AllBooks = Categorie.query.all()
        books = [book.format() for book in AllBooks]
        return jsonify({
            'success'   : True,
            'Deleted_book'  : drop_categorie.format(),
            'Total'         : Categorie.query.count(),
            'Books'         : books
        })
        
@app.route('/categories', methods = ['POST'])
def add_category():
        body = request.get_json()
        Libelle = body.get('libelle')
        category = Categorie(libelle=Libelle)
        category.insert()
        return jsonify({
            'categorie' : category.format(),
            'Total'     : Categorie.query.count()
        })
    
    
@app.route('/livres/<int:id>', methods=['PATCH'])
def modify_book(id):
    getBook = Livre.query.get(id)
    body = request.get_json()
    getBook.isbn = body.get('isbn', None)
    getBook.titre = body.get('titre', None)
    getBook.date_publication = body.get('date_publication', None)
    getBook.auteur = body.get('auteur', None)
    getBook.editeur = body.get('editeur', None)
    getBook.categorie = body.get('categorie', None)
    
    if getBook.isbn is None or getBook.titre is None or getBook.date_publication is None or getBook.auteur is None or getBook.editeur is None or getBook.categorie is None :
        abort(400) 
    else :
        getBook.update() 
        return jsonify({
            'updated_book'  : getBook.format(),
            'success'       : True
        })
        
@app.route('/categories/<int:id>', methods=['PATCH'])
def setLibelle(id):
        choix_category = Categorie.query.get(id)
        body = request.get_json()
        choix_category.libelle_categorie = body.get('libelle', None)
        if choix_category is None:
            abort(404)
        else :
            choix_category.update()
            return jsonify({
                'success'     : True,
                'setted_book' : choix_category.format()
            })
            
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success' : False,
        'Ressource'  : 'Bad Request',
    }), 400
    
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success' : False,
        'Ressource' : 'Not Found'
    }), 404

        
    
