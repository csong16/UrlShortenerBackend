import base64
import functools
import time

from flask import (
    Blueprint, current_app, flash, g, jsonify, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from UrlShortenerBackend.db import get_db

bp = Blueprint('api', __name__, url_prefix='/api')

def gen_url_id(url: str) -> str:
    # Use of timestamp for sequrity
    timestamp: str = str(time.time())
    hashcode: int = hash(timestamp + url) & 0xFFFFFFFFFFFFFFFF
    # Convert the hash integer to bytes
    hashbytes = hashcode.to_bytes((hashcode.bit_length() + 7) // 8, 'big')

    # Encode the bytes using Base64
    short_hash_string = base64.urlsafe_b64encode(hashbytes).decode('utf-8')[:-2]  # Remove padding
    current_app.logger.debug(f'Generate url_id for url `{url}` => {short_hash_string}')
    return short_hash_string

@bp.route('/urlshortener', methods=['POST'])
def urlshortener():
    try:
        data = request.get_json()
        mapped_url = data['url']
        url_id = gen_url_id(mapped_url)
        db = get_db()
        cur = db.cursor()
        res = cur.execute(f'select * from url_mapping where url_id = "{url_id}";')

        # if there is a id conflict, generate a new url_id
        while res.fetchone() is not None:
            url_id = gen_url_id(data["url"])
            res = cur.execute(f'select * from url_mapping where url_id = "{url_id}";')
        
        cur.execute(f'insert into url_mapping values ("{url_id}", "{mapped_url}");')
        db.commit()
        return jsonify({'message': 'Data received successfully', 'data': {"id": url_id}}), 200

    except Exception as e:
        current_app.logger.exception(str(e))
        return jsonify({'error': str(e)}), 400
    
