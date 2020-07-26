

# This is a Flask App which is Written in Python using Flask Modules.
# First of All imports Some Modules of Python:

from flask import Flask, render_template, request,session,redirect
from flask_sqlalchemy import SQLAlchemy
import json
import os
import math
from datetime import datetime
from werkzeug.utils import secure_filename


# SQLAchemy is used for connect our website to DataBase
# json is used for handle some usefull codes in our HTML files


