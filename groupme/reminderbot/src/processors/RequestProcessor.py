import psycopg2
from psycopg2 import sql
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
            #'bot_id': os.getenv('BOT_ID'),
            'bot_id': os.getenv('HOUSE_BOT_ID'),
            'text': msg,
        }

        requests.post(url, post_params)
        Log.debug(msg)


    def printRecentMessages(self, data):
        Log.debug("printRecentMessages {}".format(data))
        message = data['text']
        Log.debug("messages {}".format(message))
        reminderBotRq = message.split()
        if reminderBotRq[0].lower().contains("bot"):
            if reminderBotRq[1].lower() == "weather":
                cityName = ""
                for city in reminderBotRq[2:]:
                    cityName += city

                lat = str(self.getCoordinates(cityName)[0])
                lng = str(self.getCoordinates(cityName)[1])
                weather_response = requests.get('https://api.weather.gov/points/' + lat + ',' + lng + '/forecast').json()
                current_weather = weather_response['properties']['periods'][0]['detailedForecast']
                self.send_message(current_weather)

            elif reminderBotRq[1].lower() == "add":
                itemName = ""
                for item in reminderBotRq[2:]:
                    if item == "to":
                        break
                    itemName += item
                    itemName += " "

                tableName = reminderBotRq[-1]
                addUser = data['name']
                conn = psycopg2.connect(database='devlpvf6ln40ak',
                                         user='liomjizjcckrtw',
                                         password='aa34a6b5ee9b3e0d8a945a4413d5479908a1d44cbc987a4f5060840c1d680412',
                                         host='ec2-107-22-169-45.compute-1.amazonaws.com',
                                         port='5432',
                                         sslmode='require')
                cur = conn.cursor()

                createTableQuery = sql.SQL("CREATE TABLE IF NOT EXISTS {} (systemid serial PRIMARY KEY, adduser Text, item Text);") \
                    .format(sql.Identifier(tableName))

                cur.execute(createTableQuery)
                insertDataQuery = sql.SQL("INSERT INTO {} (adduser, item) VALUES(%s, %s);")\
                            .format(sql.Identifier(tableName))

                cur.execute(insertDataQuery, (addUser, itemName))
                conn.commit()
                conn.close()
            elif reminderBotRq[1].lower() == "rm":
                itemName = ""
                for item in reminderBotRq[2:]:
                    if item == "from":
                        break
                    itemName += item
                    itemName += " "

                tableName = reminderBotRq[-1]
                conn = psycopg2.connect(database='devlpvf6ln40ak',
                                        user='liomjizjcckrtw',
                                        password='aa34a6b5ee9b3e0d8a945a4413d5479908a1d44cbc987a4f5060840c1d680412',
                                        host='ec2-107-22-169-45.compute-1.amazonaws.com',
                                        port='5432',
                                        sslmode='require')
                cur = conn.cursor()
                query = sql.SQL("DELETE FROM {} WHERE item = %s;") \
                    .format(sql.Identifier(tableName))

                cur.execute(query, (itemName, ))
                conn.commit()
                conn.close()
            elif reminderBotRq[1].lower() == "show":

                tableName = reminderBotRq[-1]
                conn = psycopg2.connect(database='devlpvf6ln40ak',
                                        user='liomjizjcckrtw',
                                        password='aa34a6b5ee9b3e0d8a945a4413d5479908a1d44cbc987a4f5060840c1d680412',
                                        host='ec2-107-22-169-45.compute-1.amazonaws.com',
                                        port='5432',
                                        sslmode='require')
                cur = conn.cursor()
                if tableName == "all":
                    query = sql.SQL("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';") \
                        .format(sql.Identifier(tableName))
                else:
                    query = sql.SQL("SELECT item FROM {};") \
                        .format(sql.Identifier(tableName))

                cur.execute(query)
                tableItemContents = ""
                for table in cur.fetchall():
                    tableItemContents += table[0]
                    tableItemContents += ", "

                self.send_message("{}: {}".format(tableName, tableItemContents))
                conn.commit()
                conn.close()
            elif reminderBotRq[1].lower() == "help":
                commands = "weather: reminderbot weather <city> " \
                           "\n add: reminderbot add <item> to <list>" \
                           "\n rm: reminderbot rm <item> from <list> " \
                           "\n show: reminderbot show <list>" \
                           "\n\t reminderbot show all (lists all lists already created)"

                msg = "Commands: {}".format(commands)
                self.send_message(msg)

