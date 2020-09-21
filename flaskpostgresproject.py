from flask import Flask, render_template
from forms import RegistrationForm
app = Flask(__name__)

app.config['SECRET_KEY'] = '03690c896bd6a62327332f654cbb1ab4'

posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]

@app.route("/")
def index():
    return render_template('index.html', posts=posts)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register")
def register():
    form = RegistrationForm()
    return render_template('register.html', title='Register',form=form)

@app.route("/login")
def login():
    return render_template('about.html', title='About')


if __name__ == '__main__':
    app.run(debug = True)