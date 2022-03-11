from __future__ import print_function
import requests
import os
from urllib.parse import urlparse

from flask import Flask, render_template, request, redirect, send_file, url_for, flash, jsonify, make_response

from flask import Flask, session, Response

from s3_demo import list_files, download_file, upload_file
from boto3 import client


import time
import json
import boto3
import botocore
import nltk
# nltk.download('punkt')

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
    print(contents)
    file_list =[]
    for i in contents:
        if (".wav" in i['Key']) or (".m4a" in i['Key']):
            file_list.append(i)
    return render_template('transcribe.html', contents=file_list)


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
        content_object = s3.Object(BUCKET, "medical/Test-job.json")
        file_content = content_object.get()['Body'].read().decode('utf-8')
        json_content = json.loads(file_content)
        transcribe_content = json_content["results"]["transcripts"][0]['transcript']
        comprehend_result = comprehend(transcribe_content)
        print(transcribe_content)
        return render_template('result.html', contents=nltk.tokenize.sent_tokenize(transcribe_content), comprehend = comprehend_result)

@app.route("/delete/<filename>", methods=['GET'])
def delete(filename):
    if request.method == 'GET':
        delete_file_s3(filename)
        flash('Audio File Deleted Successfully')
        return redirect("/transcribe")

def delete_file_s3(filename):
    s3 = boto3.resource('s3')
    # s3.delete_object(Bucket=BUCKET, Key=filename)
    s3.Object(BUCKET, filename).delete()


def comprehend(text):
    client = boto3.client(service_name='comprehendmedical', region_name='us-east-1')
    result = client.detect_entities(Text= text)
    icd_result = client.infer_icd10_cm(Text=text)
    print(result)
    print(icd_result)


    health_info = dict()
    # treatment = dict()
    medical_condition = dict()
    medication = dict()

    entities = result['Entities']

    icd10_info = dict()

    icd10_entities = icd_result['Entities']
    for icd10_entity in icd10_entities:
        trait = ''
        trait_score = []
        for t in icd10_entity['Traits']:
            # print(t)
            trait = trait + t['Name'] + '_'
            # print(t['Score'])
            trait_score = trait_score+[float("{:.3f}".format(t['Score']))]
        trait = trait[:-1]
        if trait == "":
            continue
        key = trait
        icd10concept_list = []
        for concept in icd10_entity['ICD10CMConcepts']:
            icd10concept_list.append((concept['Description'], concept['Code'], concept['Score']))
        # print(icd10concept_list)

        if key in icd10_info.keys():
            icd10_info[key].append([icd10_entity['Text'], trait_score, icd10concept_list])
        else:
            icd10_info[key] = [[icd10_entity['Text'], trait_score, icd10concept_list]]


    for entity in entities:
        trait = ''
        for t in entity['Traits']:
            trait = trait + t['Name'] + '_'
        trait = trait[:-1]

        if entity['Category'] == 'PROTECTED_HEALTH_INFORMATION':
            key = entity['Type']
            if key in health_info.keys():
                health_info[key].append(entity['Text'])
            else:
                health_info[key] = [entity['Text']]
        
        if entity['Category'] == 'MEDICAL_CONDITION':
            key = trait
            if key in medical_condition.keys():
                medical_condition[key].append(entity['Text'])
            else:
                medical_condition[key] = [entity['Text']]

        if entity['Category'] == 'MEDICATION':
            key = entity['Type']
            if key in medication.keys():
                medication[key].append(entity['Text'])
            else:
                medication[key] = [entity['Text']]

    print(medical_condition)
    return [health_info, medical_condition, medication,icd10_info]


def check(filename):
    transcribe_client = boto3.client('transcribe')
    file_uri = 's3://'+BUCKET+'/'+str(filename)
    content = transcribe_file('Test-job', file_uri, transcribe_client)
    return content

# def transcribe_file(job_name, file_uri, transcribe_client):
#     transcribe_client.start_transcription_job(
#         TranscriptionJobName=job_name,
#         Media={'MediaFileUri': file_uri},
#         MediaFormat='wav',
#         LanguageCode='en-US',
#         OutputBucketName=BUCKET
#     )

#     max_tries = 60
#     while max_tries > 0:
#         max_tries -= 1
#         job = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
#         job_status = job['TranscriptionJob']['TranscriptionJobStatus']
#         if job_status in ['COMPLETED', 'FAILED']:
#             print(f"Job {job_name} is {job_status}.")
#             if job_status == 'COMPLETED':
#                 print(
#                     f"Download the transcript from\n"
#                     f"\t{job['TranscriptionJob']['Transcript']['TranscriptFileUri']}.")
#                 url_link = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
#             break
#         else:
#             print(f"Waiting for {job_name}. Current status is {job_status}.")
#         time.sleep(10)
#     response_data = requests.get('https://api.github.com')
#     delete_job = transcribe_client.delete_transcription_job(TranscriptionJobName=job_name)
#     print("job delete status", delete_job)

#     data = {"response_data": response_data.json()}
#     return data

def transcribe_file(job_name, file_uri, transcribe_client):
    transcribe_client.start_medical_transcription_job(
        MedicalTranscriptionJobName= job_name,
        LanguageCode='en-US',
        MediaFormat='wav',
        Media={
            'MediaFileUri': file_uri
        },
        OutputBucketName= 'medicalappuserbucket',
        OutputKey='Test-job.json',
        Settings= {
            "MaxSpeakerLabels": 2,
            "ShowSpeakerLabels": True,
        },
        Specialty='PRIMARYCARE',
        Type='DICTATION'
    )

    filename = ""
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
                filename = job['MedicalTranscriptionJob']['Transcript']['TranscriptFileUri']
            break
        else:
            print(f"Waiting for {job_name}. Current status is {job_status}.")
        time.sleep(10)
    
    response_data = requests.get('https://api.github.com')
    delete_job = transcribe_client.delete_medical_transcription_job(MedicalTranscriptionJobName=job_name)
    print("job delete status", delete_job)
    print("Output filename - ",filename)
    
    data = {"response_data": response_data.json()}
    return data

if __name__ == '__main__':
    # Adding test comment
    app.run(debug=True)

