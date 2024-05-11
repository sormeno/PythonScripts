import random
from datetime import datetime
from datetime import timedelta
import requests
import uuid

discipline = [   #Discipline
        'Dzień bez FPW/Newsów/SocialMedia/HBO',
        'Zasypianie bez telefonu',
        'Pójść spać o 23',
        'Wstać o 7:00',
        'Medytacja 15min przed snem',
        'Zjeść śniadanie w domu',
        'Nie jeść słodyczy',
        'Nie obgryzać paznokci/skórek',
    ]

skills = [
    [   #Sustained focus
        'Użwaj Pomodoro do pracy',
        'Switching off przed zaśnięciem',
        'Czytaj książkę',
        'Napisz artykuł na blog',
        'Obejrzyj wykład Tomasz Czajka',
        'Udemy training',
        'Zaplanuj menu na ten dzień',
        'Lichess puzzles',
        'Czytanie ukriańskich newsów',
        'Czytanie niemieckich newsów',
        'Kup model i go zbuduj',
    ],
    [
        #Communication
        'Odmówić na błahe propzycje w dobry sposób',
        'Odmówić Alicji drobnych przysług',
        'Przeprowadzić jakiś etap ewangelizacji Agile',
    ],
    [   #Sales
        'Przekonaj do czegoś Alicję',
        'Próba sprzedaży pomysłów biznesowych',
        'Self speaking english/deutsch',
        'Przekonaj znajomych na wyjście na piwo',
        'Zaproponuj jakąś zmianę w pracy',
    ],
    [   #Taking Actions
        'Praca nad pomysłem biznesowym',
        'Praca nad własnym blogiem',
        'Napraw/wynieś/zrób coś co czeka od dawna w szafie',
        'Siłownia',
        'Dodaj nowe zadania do 5skills',
        'Praca nad planem podróży do Malezji/Indonezji',
    ]
]

date = datetime.now()
today_todoist = date.strftime("%Y-%m-%d")
url = 'https://api.todoist.com/rest/v2/'
headers = {"Authorization": "Bearer 8828bec13c255fd1fb38e50b46b8e4b69fd03fc2", "Content-Type": "application/json", "X-Request-Id": str(uuid.uuid4())}

#week discipline
random_disciplines = random.sample(discipline, 2)
discipline_task = ', '.join(random_disciplines)
date += timedelta(days=1)
data = {"content": discipline_task, "due_string": date.strftime('%Y-%m-%d') + "at 8:00"}
requests.post(url+'tasks', json=data, headers=headers)

#other tasks
random.shuffle(skills)
for tasks in skills:
    date += timedelta(days=1)
    data = {"content": random.choice(tasks), "due_string": date.strftime('%Y-%m-%d') + "at 8:00"}
    requests.post(url+'tasks', json=data, headers=headers)
    data = {"content": discipline_task, "due_string": date.strftime('%Y-%m-%d') + "at 8:00"}
    requests.post(url+'tasks', json=data, headers=headers)

    