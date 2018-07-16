import psycopg2
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

                DATABASE_URL = os.environ['DATABASE_URL']
                conn = psycopg2.connect(database=DATABASE_URL,
                                             user='liomjizjcckrtw',
                                             password='aa34a6b5ee9b3e0d8a945a4413d5479908a1d44cbc987a4f5060840c1d680412',
                                             host='ec2-107-22-169-45.compute-1.amazonaws.com',
                                             port='5432',
                                             sslmode='require')
                Log.debug("Connection: {}".format(conn))

                addUser = data['name']
                sql = """INSERT INTO shared(addUser, itemName) VALUES(%s);"""
                cur = conn.createCursor()
                Log.debug("User: {} Item: {}".format(addUser, itemName))
                cur.execute(sql, (addUser, itemName))
                conn.commit()
                conn.close()