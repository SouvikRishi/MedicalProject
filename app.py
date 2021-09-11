from __future__ import print_function
import requests
import os

from flask import Flask, render_template, request, redirect, send_file, url_for, flash, jsonify, make_response

from flask import Flask, session, Response

from s3_demo import list_files, download_file, upload_file
from boto3 import client


import time
import json
import boto3
import botocore
import nltk
nltk.download('punkt')

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
BUCKET = "medicalappuserbucket"
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/')
def entry_point():
    return render_template('index.html')


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
        contents = check(filename)
        # # check() - need to update
        # print(contents)
        s3 = boto3.resource('s3')
        content_object = s3.Object(BUCKET, 'Test-job.json')
        file_content = content_object.get()['Body'].read().decode('utf-8')
        json_content = json.loads(file_content)
        transcribe_content = json_content["results"]["transcripts"][0]['transcript']
        print(transcribe_content)
        return render_template('result.html', contents=nltk.tokenize.sent_tokenize(transcribe_content))

def check(filename):
    transcribe_client = boto3.client('transcribe')
    file_uri = 's3://'+BUCKET+'/'+str(filename)
    content = transcribe_file('Test-job', file_uri, transcribe_client)
    return content

def transcribe_file(job_name, file_uri, transcribe_client):
    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': file_uri},
        MediaFormat='wav',
        LanguageCode='en-US',
        OutputBucketName=BUCKET
    )

    max_tries = 60
    while max_tries > 0:
        max_tries -= 1
        job = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        job_status = job['TranscriptionJob']['TranscriptionJobStatus']
        if job_status in ['COMPLETED', 'FAILED']:
            print(f"Job {job_name} is {job_status}.")
            if job_status == 'COMPLETED':
                print(
                    f"Download the transcript from\n"
                    f"\t{job['TranscriptionJob']['Transcript']['TranscriptFileUri']}.")
                url_link = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
            break
        else:
            print(f"Waiting for {job_name}. Current status is {job_status}.")
        time.sleep(10)
    response_data = requests.get('https://api.github.com')
    delete_job = transcribe_client.delete_transcription_job(TranscriptionJobName=job_name)
    print("job delete status", delete_job)

    data = {"response_data": response_data.json()}
    return data

# def transcribe_file(job_name, file_uri, transcribe_client):
    # transcribe_client.start_medical_transcription_job(
    #     MedicalTranscriptionJobName= job_name,
    #     LanguageCode='en-US',
    #     MediaFormat='wav',
    #     Media={
    #         'MediaFileUri': file_uri
    #     },
    #     OutputBucketName= 'medicalapplicationbucket',
    #     Settings= {
    #         "MaxSpeakerLabels": 2,
    #         "ShowSpeakerLabels": True
    #     },
    #     Specialty='PRIMARYCARE',
    #     Type='CONVERSATION'
    # )
    # filename = ""
    # max_tries = 60
    # while max_tries > 0:
    #     max_tries -= 1
    #     job = transcribe_client.get_medical_transcription_job(MedicalTranscriptionJobName=job_name)
    #     job_status = job['MedicalTranscriptionJob']['TranscriptionJobStatus']
    #     if job_status in ['COMPLETED', 'FAILED']:
    #         print(f"Job {job_name} is {job_status}.")
    #         if job_status == 'COMPLETED':
    #             print(
    #                 f"Download the transcript from\n"
    #                 f"\t{job['MedicalTranscriptionJob']['Transcript']['TranscriptFileUri']}.")
    #             filename = job['MedicalTranscriptionJob']['Transcript']['TranscriptFileUri']
    #         break
    #     else:
    #         print(f"Waiting for {job_name}. Current status is {job_status}.")
    #     time.sleep(10)
    #
    # delete_job = transcribe_client.delete_medical_transcription_job(MedicalTranscriptionJobName=job_name)
    # print("job delete status", delete_job)
    # print("Output filename - ",filename)
    #
    # return filename


if __name__ == '__main__':
    # Adding test comment
    app.run(debug=True)

