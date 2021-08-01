from scipy.io.wavfile import read, write
import io
import numpy as np
import scipy
import pymongo
import urllib
import ssl
import gridfs

client = pymongo.MongoClient("mongodb+srv://medicaltest:"+ urllib.parse.quote_plus("Souvik@1") +"@cluster0.nozgh.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",ssl_cert_reqs=ssl.CERT_NONE)
# db = client.test

# Database Name
db = client["medical_project"]

# Collection Name
col = db["audioFileUploads"]

fileName = r'Test_Audio_1.wav'

fs = gridfs.GridFS(db)

def show_files():
    fileList = []
    allAudioFiles = col.find()
    for data in allAudioFiles:
        fileList.append(data["filename"])
        # print(data["filename"])
    return fileList

def insert_audio_file(fileName):
    fileList = show_files()
    if fileName in fileList:
        print("Aborting as filename already exists")
    else:
        ref_id = fs.put( open( fileName, 'rb'))
        metadata = {"filename": fileName, "reference_id": ref_id}
        col.insert_one(metadata)

def get_audio_file(fileName):
    allAudioFiles = col.find()
    for data in allAudioFiles:
        if data["filename"] == fileName:
            ref_id = data["reference_id"]
            return fs.get(ref_id).read()

def delete_audio_file(fileName):
    allAudioFiles = col.find()
    for data in allAudioFiles:
        if data["filename"] == fileName:
            ref_id = data["reference_id"]
            # return fs.get(ref_id).read()
            query = {"filename":fileName}
            fs.delete(ref_id)
            col.delete_one(query)

# insert_audio_file(fileName)
fileName = r'audio.wav'
delete_audio_file(fileName)

