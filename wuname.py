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
    publish_event(wuname)
    return common_return(message=wuname, new_name=wuname, original_name=name, request_type='wu')


@app.route('/enterthewu/<name>', methods=['GET'])
def enter_the_wu(name):
    line_one = '{name} from this day forward'
    line_two = ' you will also be known as {wuname}'
    wuname = get_new_name(name, first_name_file="wu_adjs.txt", second_name_file="wu_nouns.txt")
    publish_event(wuname)
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
    publish_event(wuname=dwarf_name)
    return common_return(message=message, new_name=dwarf_name, original_name=name, request_type="dwarf")


@app.route('/dwarf/<name>', methods=['GET'])
def dwarf(name):
    dwarf_name = get_new_name(name=name, first_name_file='dwarf_firstname.txt', second_name_file='dwarf_lastname.txt')
    publish_event(wuname=dwarf_name)
    return common_return(message=dwarf_name, new_name=dwarf_name, original_name=name, request_type='dwarf')


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


def publish_event(wuname):
    # any value for PUBLISH_METRICS will result in True here
    if os.getenv('PUBLISH_METRICS', False):
        from google.cloud import pubsub_v1
        publisher = pubsub_v1.PublisherClient()
        topic_name = 'projects/{project_id}/topics/{topic}'.format(
            project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
            topic=os.getenv('WUNAME_RECEIVED_TOPIC_NAME', 'WUNAME_RECEIVED')
        )
        try:
            publisher.get_topic(topic_name)
        except:
            publisher.create_topic(topic_name)
        return publisher.publish(topic_name,
                                 b'Wu-Tang name generated',
                                 request_ip='{}'.format(request.remote_addr),
                                 request_path='{}'.format(request.path),
                                 request_url='{}'.format(request.url),
                                 wuname='{}'.format(wuname),
                                 request_origin='{}'.format(request.origin),
                                 request_query_string='{}'.format(request.query_string),
                                 request_user_agent='{}'.format(request.user_agent),
                                 request_original_name='{}'.format(request.path.rsplit('/', 1)[1])
                                 )
    else:
        print('metrics not enabled')


if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port)
