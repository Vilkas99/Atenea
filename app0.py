from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__) #
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' #?? archivo para base de datos(?)
db = SQLAlchemy(app) #base de datos(?)

class Entrada(db.Model): #que está entre paréntesis(?)
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id #task(?)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        name_content = request.form['content'] #para poner un nombre del denunciante en la db 
        new_name = Entrada(content=name_content)

        try:
         db.session.add(new_name) 
         db.session.commit()
         return redirect('/')  
        except:
            return 'There was an issue adding your name'

    else:
        names = Entrada.query.order_by(Entrada.date_created).all() #los ve en el orden en que fueron creados y los muestra .all=Entradas
        return render_template('index.html', names=names) #html



if __name__ == "__main__":
    app.run(debug=True)