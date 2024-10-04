from flask import Flask, render_template, redirect, jsonify

app = Flask(__name__)


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)
