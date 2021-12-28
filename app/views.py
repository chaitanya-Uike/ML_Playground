from json.decoder import JSONDecodeError
from django.http.response import HttpResponse
from django.shortcuts import render
from django.http.response import JsonResponse
from django.core.files.base import File
from . models import Document
from . import adam_optimization as ann

from random import choice
from string import ascii_uppercase, digits
import json
import pandas as pd

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Create your views here.

def home(request):
    if request.method == "POST":
        instance = Document()
        instance.session = ''.join(choice(ascii_uppercase + digits) for i in range(12))
        instance.csv = request.FILES['file']
        instance.save()

        df = pd.read_csv(os.path.join(BASE_DIR, "media", instance.csv.name))

        print("Session started: ", instance.session, instance.csv)
        data = {'session' : instance.session, 'shape' : df.shape}
        
        return JsonResponse(data)

    return render(request, "home.html")

def head(request, session):
    if request.method == "GET":
        instance = Document.objects.get(session=session)
        df = pd.read_csv(os.path.join(BASE_DIR, "media", instance.csv.name))
        head = df.head().to_json()
        return JsonResponse(head, safe=False)

def drop(request, session):
    if request.method == "POST":
        instance = Document.objects.get(session=session)
        df = pd.read_csv(os.path.join(BASE_DIR, "media", instance.csv.name))

        data = json.loads(request.body)
        dropList = list(map(int, data['dropList']))
        
        df.drop(df.columns[dropList], axis = 1, inplace = True)
        head = df.head().to_json()
        return JsonResponse(head, safe=False)

def encode(request, session):
    if request.method == "POST":
        instance = Document.objects.get(session=session)
        df = pd.read_csv(os.path.join(BASE_DIR, "media", instance.csv.name))

        data = json.loads(request.body)
        catList = list(map(int, data['catList']))
        dropList = list(map(int, data['dropList']))

        df.drop(df.columns[dropList], axis = 1, inplace = True)

        from sklearn.preprocessing import LabelEncoder
        le = LabelEncoder()
        for col in catList:
            df[df.columns[col]] = le.fit_transform(df[df.columns[col]])
        
        head = df.head().to_json()
        return JsonResponse(head, safe=False)

def saveConfig(request, session):
    if request.method == "POST":
        instance = Document.objects.get(session=session)

        data = json.loads(request.body)

        instance.config = json.dumps(data)
        instance.save()

        return HttpResponse()

def network(request, session):
    instance = Document.objects.get(session=session)

    config = instance.config
    context = {"session":instance.session,"config" : config}

    return render(request, "network.html", context)

def train(request, session):
    if request.method == "POST":
        data = json.loads(request.body)
        
        instance = Document.objects.get(session=session)
        df = pd.read_csv(os.path.join(BASE_DIR, "media", instance.csv.name))
        # preprocessing

        df = df.dropna(axis=0)

        catList = list(map(int, data['config']['catList']))
        dropList = list(map(int, data['config']['dropList']))

        df.drop(df.columns[dropList], axis = 1, inplace = True)

        from sklearn.preprocessing import LabelEncoder
        le = LabelEncoder()
        for col in catList:
            df[df.columns[col]] = le.fit_transform(df[df.columns[col]])
        
        n_samples = data['config']['n_samples']
        X_start = data['config']['X_start']
        X_end = data['config']['X_end']
        Y_col = data['config']['Y_col']

        X = df.iloc[0: n_samples, X_start:X_end+1].values
        Y = df.iloc[0:n_samples, Y_col].values

        Y = Y.reshape(-1,1)

        if data['config']['classification'] == 'multiclass':
            from sklearn.preprocessing import OneHotEncoder
            ohe = OneHotEncoder(categories='auto', sparse=False)
            Y = ohe.fit_transform(Y)
        
        testSize = data['config']['test_size'] / 100
        from sklearn.model_selection import train_test_split
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=testSize, random_state=1)

        layers_dims = data['layersDims']
        classification = data['config']['classification']
        learning_rate= data['alpha']
        epochs=data['epochs']
        batch=data['batch']
        lambd=data['lambda']
        beta1=data['beta1']
        beta2=data['beta2']
        epsilon = 1e-8

        context = ann.train_minibatch(X_train, Y_train, X_test, Y_test, layers_dims, classification, learning_rate, epochs, batch, lambd, beta1, beta2,epsilon)

        parameters = {}
        for key, value in context['parameters'].items():
            parameters[key] = value.tolist()

        dict_data = {
            "Parameters" : parameters,
            "config" : data['config']
        }

        a_file = open(f"parameters-{session}.json", "w+")
        json.dump(dict_data, a_file)

        instance.params = File(a_file)
        instance.save()
        a_file.close()
        os.remove(f"parameters-{session}.json")
        
        ctx = {"file_url" : instance.params.url, "train_cost" : context['train_cost'],"test_cost" : context['test_cost'], "a_train" : context['a_train'], "a_test" : context['a_test'],}

        return JsonResponse(ctx)


def close(request):
    if request.method == "POST":
        data = json.loads(request.body)
        instance = Document.objects.get(session=data['session'])
        print("session-closed: ", data['session'], instance.csv)
        instance.delete()
    return HttpResponse()