from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import choice


app = Flask(__name__)
SECRET_KEY = 'TopSecretAPIKey'

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


# Home route
@app.route("/")
def home():
    return render_template("index.html")


# Returns details about a random cafe
@app.route('/random')
def get_random_cafe():
    all_cafes = db.session.query(Cafe).all()
    random_cafe = choice(all_cafes)
    return jsonify(cafe=random_cafe.to_dict())


# Returns the details of all cafes in the database
@app.route('/all')
def get_all_cafes():
    all_cafes = db.session.query(Cafe).all()
    all_cafes_dictionaries = []
    for cafe in all_cafes:
        all_cafes_dictionaries.append(cafe.to_dict())
    return jsonify(cafe=all_cafes_dictionaries)


# Receives a location parameter and returns details about cafes available in that location
@app.route('/search')
def search_cafe():
    loc = request.args['loc']
    cafes_at_location = db.session.query(Cafe).filter_by(location=loc).all()
    cafes_at_location = [cafe.to_dict() for cafe in cafes_at_location]
    if cafes_at_location:
        return jsonify(cafe=cafes_at_location)
    return jsonify(error={'Not Found': 'Sorry we don\'t have a cafe at that location.'})


# Changes an int data type to boolean
def make_bool(val: int) -> bool:
    return bool(int(val))


# Allows to add a cafe to the database
@app.route('/add', methods=['POST', 'GET'])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        has_sockets=make_bool(request.form.get("has_sockets")),
        has_toilet=make_bool(request.form.get("has_toilet")),
        has_wifi=make_bool(request.form.get("has_wifi")),
        can_take_calls=make_bool(request.form.get("can_take_calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(result={'action successful': 'The new cafe was added to the database.'})


# Changes the cofee price of a certain cafe
@app.route('/update-price/<int:cafe_id>', methods=['PATCH'])
def change_coffee_price(cafe_id):
    cafe_to_change = db.session.query(Cafe).filter_by(id=cafe_id).first()
    if cafe_to_change is not None:
        cafe_to_change.coffee_price = request.args.get('new_price')
        db.session.commit()
        return jsonify(result={'action successful': 'The cafe price for the cafe has been updated.'})
    else:
        return jsonify(result={'Error': 'Sorry the cafe id provided does not exist.'}), 404


# Deletes a cafe from the database
@app.route('/report-closed/<int:cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id):
    if SECRET_KEY == request.args.get('secret_key'):
        cafe_to_delete = Cafe.query.get(cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(result={'Action Successful': 'The cafe was removed from the database.'})
        else:
            return jsonify(result={'Error': 'The id provided is not in the database.'}), 404
    else:
        return jsonify(result={'Error': 'The api key provided is not valid. Action denied.'}), 403


if __name__ == '__main__':
    app.run(debug=True)
