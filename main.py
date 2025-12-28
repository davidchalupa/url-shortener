import hashlib
import string

from flask import Flask, jsonify, request, redirect

from db.session import SessionLocal
from db.models import Shorthand


app = Flask(__name__)

# auxiliary variables for Base62 encoding
BASE62_ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase
BASE = 62

def normalize_url(url: str) -> str:
    """
    Ensure the URL has a scheme (http:// or https://).
    If missing, prepend http:// by default.
    """
    url = url.strip()
    if not url:
        raise ValueError("URL cannot be empty")

    if url.startswith(("http://", "https://")):
        return url

    # Default to http:// if no scheme
    return "http://" + url

def create_short_url_code(full_url: str) -> str:
    """
    Creates a shortened code version of the URL from the entire URL.
    """
    if not isinstance(full_url, str):
        raise TypeError("value must be a string")

    # hashing
    url_hash = hashlib.sha256(full_url.encode("utf-8")).digest()

    # converting the hash into a big integer
    hash_as_bigint = int.from_bytes(url_hash, byteorder="big")

    # encoding the hash digest as Base62
    url_hash_base62 = sha256_to_base62(hash_as_bigint)

    # returning the first 8 characters
    return url_hash_base62[:8]


def sha256_to_base62(hash_as_bigint: int) -> str:
    """
    Compute SHA-256 of a string and return a base62-encoded string.
    """
    # encode integer to base62
    if hash_as_bigint == 0:
        return BASE62_ALPHABET[0]

    encoded = []
    while hash_as_bigint > 0:
        hash_as_bigint, rem = divmod(hash_as_bigint, BASE)
        encoded.append(BASE62_ALPHABET[rem])

    return "".join(reversed(encoded))


def insert_shorthand(full_url: str, short_url_code: str):
    """
    Inserts our shortened URL code into the database.
    :param full_url: Full url shortened.
    :param short_url_code: Shortened URL code.
    :return:
    """
    with SessionLocal() as session:
        shorthand = Shorthand(
            full_url=full_url,
            short_url_code=short_url_code,
        )
        session.add(shorthand)
        session.commit()


@app.route("/shorten", methods=["POST"])
def shorten():
    """
    POST /shorten
    Expects JSON body:
    {
        "url": "https://www.example.com"
    }
    """
    data = request.get_json(silent=True)

    # invalid JSON request
    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    full_url = data.get("url")

    # invalid name field
    if full_url is None or not isinstance(full_url, str) or not full_url.strip():
        return jsonify({
            "error": "Field 'url' is required and must be a non-empty string"
        }), 400

    # ToDo: validation whether it really is a url

    # normalizing the URL in case of no protocol prepended
    full_url_normalized = normalize_url(full_url)

    short_url_code = create_short_url_code(full_url_normalized)

    # ToDo: handling repeated inserts - currently it gives an HTTP 500
    # ToDo: storing also created_time and expiration_time

    # ToDo: adding salt into the URL creation, potential retries

    # inserting our short code into the database
    insert_shorthand(full_url_normalized, short_url_code)

    # success
    return jsonify({
        "short_url": short_url_code
    }), 200


@app.route("/<string:short_code>", methods=["GET"])
def redirect_short_url(short_code: str):
    """
    Lookup a short URL code in the database and return the full URL.
    Example: GET http://127.0.0.1:5000/eF7258ae
    Returns HTTP 302 if found, 404 if not.
    """
    with SessionLocal() as session:
        # querying the database for the short code
        shorthand = session.query(Shorthand).filter_by(
            short_url_code=short_code
        ).first()

        # url not found handler
        if not shorthand:
            return jsonify({
                "error": f"No URL found for short code '{short_code}'"
            }), 404

        # Redirect to the full URL (HTTP 302)
        return redirect(shorthand.full_url)


if __name__ == "__main__":
    # for now using 127.0.0.1 for testing
    # for production we might need 0.0.0.0 with some web server / proxy (WSGI or similar)
    app.run(host="127.0.0.1", port=5000, debug=False)
