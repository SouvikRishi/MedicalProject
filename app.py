from __future__ import print_function

import os

from flask import Flask, render_template, request, redirect, send_file, url_for, flash, jsonify, make_response

from flask import Flask, session

from s3_demo import list_files, download_file, upload_file

import time
import json
import boto3
import botocore

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
UPLOAD_FOLDER = "uploads"
BUCKET = "medicalapplicationbucket"


@app.route('/')
def entry_point():
    return 'Hello World!'


@app.route("/storage")
def storage():
    contents = list_files(BUCKET)
    return render_template('storage.html', contents=contents)

@app.route("/transcribe")
def transcribe():
    contents = list_files(BUCKET)
    return render_template('transcribe.html', contents=contents)


@app.route("/upload", methods=['POST'])
def upload():
    if request.method == "POST":
        f = request.files['file']
        f.save(f.filename)
        upload_file(f"{f.filename}", BUCKET)
        flash('Audio File Uploaded Successfully')
        return redirect("/transcribe")


@app.route("/download/<filename>", methods=['GET'])
def download(filename):
    if request.method == 'GET':
        output = download_file(filename, BUCKET)
        contents = check()  
        # check() - need to update
        return render_template('result.html', contents=contents)

def check():
    transcribe_client = boto3.client('transcribe')
    file_uri = 's3://medicalapplicationbucket/New Recording 11.wav'
    transcribe_file('Test-job', file_uri, transcribe_client)

def transcribe_file(job_name, file_uri, transcribe_client):
    transcribe_client.start_medical_transcription_job(
        MedicalTranscriptionJobName= job_name,
        LanguageCode='en-US',
        MediaFormat='wav',
        Media={
            'MediaFileUri': file_uri
        },
        OutputBucketName= 'medicalapplicationbucket',
        Settings= {
            "MaxSpeakerLabels": 2,
            "ShowSpeakerLabels": True
        },
        Specialty='PRIMARYCARE',
        Type='CONVERSATION'
    )

    max_tries = 60
    while max_tries > 0:
        max_tries -= 1
        job = transcribe_client.get_medical_transcription_job(MedicalTranscriptionJobName=job_name)
        job_status = job['MedicalTranscriptionJob']['TranscriptionJobStatus']
        if job_status in ['COMPLETED', 'FAILED']:
            print(f"Job {job_name} is {job_status}.")
            if job_status == 'COMPLETED':
                print(
                    f"Download the transcript from\n"
                    f"\t{job['MedicalTranscriptionJob']['Transcript']['TranscriptFileUri']}.")
            break
        else:
            print(f"Waiting for {job_name}. Current status is {job_status}.")
        time.sleep(10)


if __name__ == '__main__':
    app.run(debug=True)

