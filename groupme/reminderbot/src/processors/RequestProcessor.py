import requests
import os
from ..controllers.Log import Log
from ..database.PostgresConnector import PostgresConnector


class RequestProcessor:

    def __init__(self):
        print("Processing Requests...")


    def getResponse(self, request_params):

        response = requests.get('https://api.groupme.com/v3/groups/41786620/messages', request_params)
        return response

    def getCoordinates(self, city):
        geocode_response = requests.get("http://maps.google.com/maps/api/geocode/json?address=" + city).json()
        coordinates = geocode_response['results'][0]['geometry']['location']
        latitude = coordinates['lat']
        longitude = coordinates['lng']
        return latitude, longitude


    def send_message(self, msg):
        url = 'https://api.groupme.com/v3/bots/post'

        post_params = {
            'bot_id': os.getenv('BOT_ID'),
            'text': msg,
        }

        botRequest = requests.post(url, post_params)
        msg = "{}".format(botRequest)


    def printRecentMessages(self, data):
        Log.debug("printRecentMessages {}".format(data))
        message = data['text']
        Log.debug("messages {}".format(message))
        reminderBotRq = message.split()
        if reminderBotRq[0].lower() == "reminderbot":
            if reminderBotRq[1].lower() == "weather":
                cityName = ""
                for city in reminderBotRq[2:]:
                    cityName += city

                lat = str(self.getCoordinates(cityName)[0])
                lng = str(self.getCoordinates(cityName)[1])
                weather_response = requests.get('https://api.weather.gov/points/' + lat + ',' + lng + '/forecast').json()
                current_weather = weather_response['properties']['periods'][0]['detailedForecast']
                Log.debug("WeatherRs: {}".format(current_weather))
                self.send_message(current_weather)

            elif reminderBotRq[1].lower() == "weather":
                itemName = ""
                for item in reminderBotRq[2:]:
                    if item != "to":
                        item += itemName

                addUser = data['name']
                sql = """INSERT INTO shared(addUser, itemName) VALUES(%s) RETURNING vendor_id;"""
                database = PostgresConnector()
                cur = database.createCursor()
                cur.execute(sql, (addUser, itemName))
                database.commit()