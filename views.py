from django.shortcuts import render, redirect  
from django.http import JsonResponse
import openai
from django.contrib.auth.models import User
from django.contrib import auth
import json  
import logging

openai_api_key = ""
openai.api_key = openai_api_key

predefined_text = "Provide me a food recipe that can be prepared from the given items such as "
suffix_text = ". Summarize everything in 150 words and provide the answer in bullet points format and every sentence should be in another line. Please press Enter button after every fullstop. Give the name of the recipe in first two words of the response. Note the recipe name should only and only be two words"

wo = []

def ask_openai(user_message, option):
    message_new="The food item you suggest should be of "
    message_new1=' cuisine'
    try:
        user_message= predefined_text+user_message+ suffix_text+ message_new +option+ message_new1
        response1= openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": predefined_text},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7
        )
        answer1 = response1['choices'][0]['message']['content'].strip()
        
        
        recipe_name = " ".join(answer1.split()[:2])

        # Second query for an item that can be eaten along with the first recipe
        second_query = f"Provide me a recipe of a dish that can be eaten along with {recipe_name}."
        response2 = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": predefined_text},
                {"role": "user", "content": second_query}
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7
        )
        answer2 = response2['choices'][0]['message']['content'].strip()

        return answer1, answer2
    except Exception as e:
        logging.error("Error in ask_openai function: ", e)
        return "An error occurred while processing your request. Please try again later.", ""

def chatbot(request):
    if request.method=='POST':
        try:
            data=json.loads(request.body)
            message=data.get('message')
            option1=data.get('option1')
            if not message:
                return JsonResponse({'error': 'No message provided'}, status=400)

            if message.lower()=='yes':
                message= 'Give me the recipe of a dish related to '
                response1, response2 = ask_openai(message, option1)
                return JsonResponse({'message': message, 'response1': response1, 'response2': response2})

            response1, response2=ask_openai(message, option1)
            return JsonResponse({'message': message, 'response1': response1, 'response2': response2})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return render(request, 'chatbot.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')  
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method =='POST':
        username =request.POST['username']
        email =request.POST['email']
        password1=request.POST['password1']
        password2=request.POST['password2']

        if password1== password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')  
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = "Passwords don't match"
            return render(request, 'register.html', {'error_message': error_message})
    else:
        return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login') 
