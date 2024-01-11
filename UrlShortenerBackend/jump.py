import base64
import functools
import time

from flask import (
    Blueprint, current_app, flash, g, jsonify, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from UrlShortenerBackend.db import get_db

bp = Blueprint('jump', __name__, url_prefix='/j')

def fix_external_url(url):
    # Check if the URL starts with 'http://' or 'https://'
    if not url.startswith(('http://', 'https://')):
        # If not, assume 'http://' and add it to the URL
        url = 'http://' + url
    return url

@bp.route("/<string:id>", methods=["GET"])
def urlshortener_redirect(id: str):
    # retrive the original url
    db = get_db()
    cur = db.cursor()
    res = cur.execute(f'select * from url_mapping where url_id="{id}";').fetchone()
    if res is not None:
        return redirect(fix_external_url(res['mapped_url']))