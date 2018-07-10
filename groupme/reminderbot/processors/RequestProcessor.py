import requests
import time

class RequestProcessor:

    def __init__(self):
        print("Processing Requests...")

    def getRecentMessages(self):
        request_params = {'token': 'SlxENrNwb5ZSWVlRk2H5SyKIHjDQyg6pGYmNHqnS'}
        response_messages = requests.get('https://api.groupme.com/v3/groups/41786620/messages',
                                         request_params).json()['response']['messages']
        return response_messages

    def printRecentMessages(self):
        location_name = 'San Jose, CA'
        location_coords = {'x': '37.3382', 'y': '-121.8863'}

        while True:
            messages = self.getRecentMessages();
            for message in messages:
                if message['text'] == "weather":
                    weather_response = requests.get('https://api.weather.gov/points/' + location_coords['x'] + ',' + location_coords['y'] + '/forecast').json()
                    current_weather = weather_response['properties']['periods'][0]['detailedForecast']
                    print ('Weather for ' + location_name + ': ' + current_weather)
                    request_params['since_id'] = message['id']
                    break

                print(message['text'])

            time.sleep(5)

