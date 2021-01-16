from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, url_for, request, redirect, jsonify
import json
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import unpad  # for decryption
from base64 import b64decode
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
import os
import re


'''                -------------------- AES - CBC  -----------------------                 '''

def encriptar(plaintext, iv):
    pt_bytes = bytes(plaintext, 'utf-8')
    iv_bytes = bytes(iv, 'utf-8')
    key = b64encode(get_random_bytes(16))
    print(key)
    # Si quitas el iv, se genera random
    cipher = AES.new(key, AES.MODE_CBC, iv_bytes)
    ct_bytes = cipher.encrypt(pad(pt_bytes, AES.block_size))
    iv2 = cipher.iv.decode('utf-8')
    ct = b64encode(ct_bytes).decode('utf-8')
    key_str = key.decode('utf-8')
    result = json.dumps({
        'ciphertext': ct,
        "iv": iv2,
        'key': encrypt_subs(key_str)}, ensure_ascii=False)  # "iv":iv2
    return result

def desencriptar(ciphertext, iv, key_str):
    try:
        key_str = decrypt_subs(key_str)
        print(key_str)
        ct_bytes = bytes(ciphertext, 'utf-8')
        ct_bytes = b64decode(ct_bytes)
        # print(ct_bytes)
        iv_bytes = bytes(iv, 'utf-8')
        key = bytes(key_str, 'utf-8')
        cipher = AES.new(key, AES.MODE_CBC, iv_bytes)
        pt_bytes = unpad(cipher.decrypt(ct_bytes), AES.block_size)
        plaintext = pt_bytes.decode('utf-8')
        result = json.dumps(plaintext, ensure_ascii=False)
        return result
    except:
        return json.dumps({"message": "Operación fallida"}, ensure_ascii=False)



'''           -------------------- SUBSTITUTION CIPHER -----------------------                    '''

alphabet = ['A', 'a', 'B', 'b', 'C', 'c', 'D', 'd', 'E', 'e', 'F', 'f', 'G', 'g', 'H', 'h', 'I', 'i', 'J', 'j', 'K', 'k', 'L', 'l', 'M', 'm', 'N', 'n', 'Ñ',
            'ñ', 'O', 'o', 'P', 'p', 'Q', 'q', 'R', 'r', 'S', 's', 'T', 't', 'U', 'u', 'V', 'v', 'W', 'w', 'X', 'x', 'Y', 'y', 'Z', 'z', '=', '+', '-', '*', '/', '|']
key = ['I', 'E', 'k', 'q', 'P', 'B', 'V', 'a', 'M', 'n', 'N', 'u', 't', 'O', 'j', 'T', 'R', 'Q', '|', 's', 'X', 'z', 'w', 'A', 'b', '=', 'L', 'm', '*',
       'G', 'y', 'U', 'c', '+', 'h', 'g', 'Z', 'e', 'H', 'Y', '/', 'x', 'C', 'J', 'W', 'r', 'v', 'S', 'ñ', 'Ñ', 'D', 'F', '-', 'K', 'o', 'i', 'p', 'l', 'd', 'f']

def encrypt_subs(word):
    ct = ""
    for character in word:
        if character in alphabet:
            pos = int(alphabet.index(character))
            new_char = key[pos]
            ct += new_char
        else:
            ct += character
    return ct


def decrypt_subs(word):
    pt = ""
    for character in word:
        if character in key:
            pos = int(key.index(character))
            new_char = alphabet[pos]
            pt += new_char
        else:
            pt += character
    return pt


'''                     --------------------API-----------------------                    '''

#Initialize Flask app
app = Flask(__name__)

#Initialize Firestore DB
cred = credentials.Certificate("key.json")
default_app = initialize_app(cred)
db = firestore.client()
todo_ref = db.collection("usuarios")


@app.route("/denuncia/<id>", methods=["GET"])
def obtenerDenuncia(id):
    try:
        todo_id = id        
        todo = todo_ref.document(todo_id).get()
        denuncia_todo = todo.to_dict()
        denuncia = denuncia_todo["denuncia"]
        ciphertext = re.findall('"ciphertext": "(\S+)"', denuncia)
        iv = re.findall('"iv": "(\S+)"', denuncia)
        key = re.findall('"key": "(\S+)"', denuncia)
        return desencriptar(ciphertext[0], iv[0], key[0]), 200
    except:
        return jsonify({"message":"An Error Ocurred"})

@app.route('/denuncia', methods=["GET"])
def obtenerDenuncias():
    all_todos = []
    for doc in todo_ref.stream():
        denuncia_todo = doc.to_dict()
        denuncia = denuncia_todo["denuncia"]
        print(denuncia)
        ciphertext = re.findall('"ciphertext": "(\S+)"', denuncia)
        print(ciphertext)
        iv = re.findall('"iv": "(\S+)"', denuncia)
        print(iv)
        key = re.findall('"key": "(\S+)"', denuncia)
        print(key)
        print(desencriptar(ciphertext[0], iv[0], key[0]))
        all_todos.append(desencriptar(ciphertext[0], iv[0], key[0]))
    return jsonify(all_todos), 200


@app.route('/denuncia', methods=["POST"])
def crearDenuncia():
    try:
        id = request.json["id"] #Leonardo Contreras / Karla Martínez
        nueva_denuncia =  request.json["denunciante"] + "/" + request.json["denunciado"]
        #"id": request.json["id"],
        #"denunciado": encriptar(request.json["denunciado"], request.json["id"])
        denuncia = {"denuncia": encriptar(nueva_denuncia, id)}
        todo_ref.document(id).set(denuncia) #request.json
        return jsonify({"message":"Denuncia hecha correctamente"}), 200
    except:
        return jsonify({"message": "There was an issue submitting your form"})


if __name__ == "__main__":
    app.run(debug=True)