from project5 import app
from flask import request, render_template, jsonify
messageData = [{}]
userData = ["bot"]
@app.route('/flask')
def hello_world(name=None):
    return render_template('index.html', name=name)

@app.route('/flask/add', methods=['GET', 'POST'])
def add():
    print("in add")
    print(request.method)
    if request.method == 'POST':
        print("in post")
        content = request.get_json(force=True)
        print(content)
        sum = 0
        for num in content['add']:
            sum = sum + num
        return jsonify({"result":sum})
    return jsonify({"result":0})

@app.route('/flask/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'POST':
        content = request.get_json(force=True)
        messageData.append(content)
        return jsonify({"Message Posted":1})
    if request.method == 'GET':
        return jsonify({"d":messageData});

@app.route('/flask/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        content = request.get_json(force=True)
        userData.append(content)
        return jsonify({"User Posted":1})
    if request.method == 'GET':
        return jsonify({"d":userData});


        

