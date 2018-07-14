import os
import requests
import time

class RequestProcessor:

    def __init__(self):
        print("Processing Requests...")

    def getResponse(self, request_params):

        response = requests.get('https://api.groupme.com/v3/groups/41786620/messages',
                                         request_params)
        return response

    def getCoordinates(self, city):
        geocode_response = requests.get("http://maps.google.com/maps/api/geocode/json?address=" + city).json()
        coordinates = geocode_response['results'][0]['geometry']['location']
        latitude = coordinates['lat']
        longitude = coordinates['lng']
        return latitude, longitude

    def printRecentMessages(self):
        request_params = {'token': os.getenv("ACCESS_TOKEN")}

        while True:
            response = self.getResponse(request_params);
            if response.status_code == 200:
                messages = response.json()['response']['messages']
                for message in messages:
                    reminderBotRq = message['text'].split()
                    if reminderBotRq[0].lower() == "reminderbot":
                        if reminderBotRq[1].lower() == "weather":
                            city = ""
                            for cityName in reminderBotRq[2:]:
                                city += cityName

                            lat = str(self.getCoordinates(cityName)[0])
                            lng = str(self.getCoordinates(cityName)[1])
                            weather_response = requests.get('https://api.weather.gov/points/' + lat + ',' + lng + '/forecast').json()
                            current_weather = weather_response['properties']['periods'][0]['detailedForecast']

                            # Send the response to the group
                            post_params = { 'bot_id' : os.getenv("BOT_ID"), 'text': current_weather }
                            requests.post('https://api.groupme.com/v3/bots/post', post_params)
                            request_params['since_id'] = message['id']
                            break