#!/usr/bin/env python

from flask import Blueprint
from flask import Flask, redirect, url_for, session, request, jsonify

from main import google

frontend = Blueprint('frontend', __name__)
