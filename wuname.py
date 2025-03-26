#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/wuami/<name>', methods=['GET'])
def wu_am_i(name):
    wuname = get_new_name(name, first_name_file="wu_adjs.txt", second_name_file="wu_nouns.txt")
    return common_return(message=wuname, new_name=wuname, original_name=name, request_type='wu')


@app.route('/enterthewu/<name>', methods=['GET'])
def enter_the_wu(name):
    line_one = '{name} from this day forward'
    line_two = ' you will also be known as {wuname}'
    wuname = get_new_name(name, first_name_file="wu_adjs.txt", second_name_file="wu_nouns.txt")
    line_one = line_one.format(name=name)
    line_two = line_two.format(wuname=wuname)
    message = '''{line_one}\n{line_two}'''.format(line_one=line_one, line_two=line_two)
    return common_return(message, wuname, name, request_type='wu')


@app.route('/durinsfolk/<name>', methods=['GET'])
def durins_folk(name):
    dwarf_name = get_new_name(name=name, first_name_file='dwarf_firstname.txt', second_name_file='dwarf_lastname.txt')
    message = '''By the beard of Durin, {name}, you will henceforth be known as {dwarf_name}!
May your days be filled with mining precious metals, regaling us with tales 
of adventure, and upholding the honor of Durin's folk!'''.format(name=name, dwarf_name=dwarf_name)
    return common_return(message=message, new_name=dwarf_name, original_name=name, request_type="dwarf")


@app.route('/dwarf/<name>', methods=['GET'])
def dwarf(name):
    dwarf_name = get_new_name(name=name, first_name_file='dwarf_firstname.txt', second_name_file='dwarf_lastname.txt')
    return common_return(message=dwarf_name, new_name=dwarf_name, original_name=name, request_type='dwarf')


@app.route('/hobbit/<name>', methods=['GET'])
def hobbit(name):
    hobbit_name = get_new_name(name=name, first_name_file='hobbit_firstname.txt', second_name_file='hobbit_lastname.txt')
    return common_return(message=hobbit_name, new_name=hobbit_name, original_name=name, request_type='hobbit')


@app.route('/shirefolk/<name>', methods=['GET'])
def shirefolk(name):
    hobbit_name = get_new_name(name=name, first_name_file='hobbit_firstname.txt', second_name_file='hobbit_lastname.txt')
    message = f'''Welcome to the Shire my dear friend, {name}! It's a pleasure to have you amongst our peaceful and 
jolly Hobbit folk. I am honored to bestow upon you a Hobbit name, which shall be known as your honorary title in our 
beloved Shire. Henceforth, you shall be called {hobbit_name}, a name that represents your kinship with our merry 
Hobbiton-folk and your esteemed place in our warm-hearted community. May you find joy and merriment in the simple 
pleasures of the Shire, and may your days be filled with the mirth and laughter that our Hobbit-kind is known for. 
Welcome, {hobbit_name}, to the warm embrace of the Shire!'''
    return common_return(message=message, new_name=hobbit_name, original_name=name, request_type='hobbit')


@app.route('/hackers/<name>', methods=['GET'])
def hackers(name):
    hacker_name = get_new_name(name=name, first_name_file='hacker_firstpart.txt', second_name_file='hacker_lastpart.txt')
    message = f'''Welcome to our world, {name}. We're the Hackers, the elite of the digital underground. 
We're the ones who push the boundaries, break the rules, and make our own reality. This is our playground, 
where we dance with code, ride the information highway, and unlock doors that others can't even see. 
Get ready to dive deep into the virtual abyss, where we trade in secrets, exploit vulnerabilities, and uncover hidden 
truths. Here, your skills with a keyboard and your imagination are your weapons, and the possibilities are limitless. 
So buckle up, {hacker_name}, because you're about to experience a whole new level of electrifying adventure in the 
world of Hackers!'''
    return common_return(message=message, new_name=hacker_name, original_name=name, request_type='hacker')


@app.route('/hacker/<name>', methods=['GET'])
def hacker_simple(name):
    hacker_name = get_new_name(name=name, first_name_file='hacker_firstpart.txt', second_name_file='hacker_lastpart.txt')
    return common_return(message=hacker_name, new_name=hacker_name, original_name=name, request_type='hacker')


def common_return(message, new_name, original_name, request_type):
    if request_wants_type('application/json'):
        return jsonify({'message': message})
    elif request_wants_type('text/plain'):
        return message
    elif request_wants_type('application/xml'):
        return render_template('{}_response.xml'.format(request_type),
                               message=message,
                               )
    else:
        return render_template('{}_response.html'.format(request_type),
                               message=message,
                               new_name=new_name,
                               original_name=original_name
                               )


def get_new_name(name, first_name_file, second_name_file):
    import random
    seed = 1013

    for i, char in enumerate(name.lower()):
        seed += ord(char) * (i + 1)
    random.seed(a=seed, version=2)

    first_names = read_file('assets/{}'.format(first_name_file))

    last_names = read_file('assets/{}'.format(second_name_file))

    return "{first} {last}".format(
        first=first_names[random.randint(0, len(first_names) - 1)],
        last=last_names[random.randint(0, len(last_names) - 1)]
    )


def read_file(fname):
    words = []
    with open(fname) as f:
        for i, word in enumerate(f):
            words.append(word.rstrip())
    return words


def request_wants_type(type):
    best = request.accept_mimetypes \
        .best_match([type, 'text/html'])
    return best == type and \
           request.accept_mimetypes[best] > \
           request.accept_mimetypes['text/html']


if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port)
