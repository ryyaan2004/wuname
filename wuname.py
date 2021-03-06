#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

LINE_ONE = '%s from this day forward'
LINE_TWO = ' you will also be known as '


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/wuami/<name>', methods=['GET'])
def wu_am_i(name):
    wuname = get_wu_name(name)
    publish_event(wuname)
    return common_return(wuname, '', '', wuname, name)


@app.route('/enterthewu/<name>', methods=['GET'])
def enter_the_wu(name):
    wuname = get_wu_name(name)
    publish_event(wuname)
    message = LINE_ONE % name + LINE_TWO + wuname
    return common_return(message, LINE_ONE % name, LINE_TWO, wuname, name)


def common_return(message, line_one, line_two, wuname, original_name):
    if request_wants_type('application/json'):
        return jsonify({'message': message})
    elif request_wants_type('text/plain'):
        return message
    elif request_wants_type('application/xml'):
        return render_template('response.xml', message=message)
    else:
        return render_template('response.html',
                               line_one=line_one,
                               line_two=line_two,
                               wuname=wuname,
                               original_name=original_name
                               )


def get_wu_name(name):
    import random
    seed = 1013

    for i, char in enumerate(name.lower()):
        seed += ord(char) * (i + 1)
    random.seed(a=seed, version=2)

    wu_adjs = read_file('assets/wu_adjs.txt')

    wu_nouns = read_file('assets/wu_nouns.txt')

    return "{adj} {noun}".format(
        adj=wu_adjs[random.randint(0, len(wu_adjs) - 1)],
        noun=wu_nouns[random.randint(0, len(wu_nouns) - 1)]
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
    from google.cloud import pubsub_v1
    if os.getenv('PUBLISH_METRICS', False):
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
