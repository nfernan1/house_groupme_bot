import psycopg2
from psycopg2 import sql
import requests
import os
from ..controllers.Log import Log
from ..database.PostgresConnector import PostgresConnector
from pygeocoder import Geocoder
import pyowm


class RequestProcessor:

    def __init__(self):
        print("Processing Requests...")


    def getResponse(self, request_params):

        response = requests.get('https://api.groupme.com/v3/groups/41786620/messages', request_params)
        return response

    def getCoordinates(self, city):
        geocode = Geocoder.geocode(city)
        coordinates = geocode.coordinates
        return coordinates


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
        if "house" in reminderBotRq[0].lower():
            if reminderBotRq[1].lower() == "weather":
                cityName = ""
                for city in reminderBotRq[2:]:
                    cityName += city

                lat = float(self.getCoordinates(cityName)[0])
                lng = float(self.getCoordinates(cityName)[1])
                owm = pyowm.OWM(os.getenv('OWM_KEY'))
                obs = owm.weather_at_coords(lat, lng)
                w = obs.get_weather()

                temp = w.get_temperature('fahrenheit')['temp']
                temp_min = w.get_temperature('fahrenheit')['temp_min']
                temp_max = w.get_temperature('fahrenheit')['temp_max']
                status = w.get_detailed_status()
                wind_speed = w.get_wind()['speed']
                weather_response = "Today Temp: {}; Low: {}; High: {} with {} and wind speed of {} mph"\
                                    .format(temp, temp_min, temp_max, status, wind_speed)
                self.send_message(weather_response)
                return weather_response, 200

            elif reminderBotRq[1].lower() == "add":
                itemName = ""
                for item in reminderBotRq[2:]:
                    if item == "to":
                        break
                    itemName += item
                    itemName += " "
                itemName = itemName.rstrip()
                idxToTableName = reminderBotRq.index("to") + 1
                tableName = ""
                for tableToAddName in reminderBotRq[idxToTableName:]:
                    tableName += tableToAddName
                    tableName += " "
                tableName = tableName.rstrip()
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
                msg = "Successfully {} {} to {}".format("added", itemName, tableName)
                self.send_message(msg)
                return msg, 200

            elif reminderBotRq[1].lower() == "rm":
                itemName = ""
                for item in reminderBotRq[2:]:
                    if item == "from":
                        break
                    itemName += item
                    itemName += " "
                itemName = itemName.rstrip()
                idxToTableName = reminderBotRq.index("from") + 1
                tableName = ""
                for tableToAddName in reminderBotRq[idxToTableName:]:
                    tableName += tableToAddName
                    tableName += " "
                tableName = tableName.rstrip()
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

                countRowQuery = sql.SQL("SELECT COUNT(*) FROM {} WHERE systemid IS NOT NULL;") \
                    .format(sql.Identifier(tableName))

                cur.execute(countRowQuery)
                rowCount = cur.fetchone()
                if rowCount[0] == 0:
                    countRowQuery = sql.SQL("DROP TABLE {} ;") \
                        .format(sql.Identifier(tableName))

                    cur.execute(countRowQuery)

                conn.commit()
                conn.close()
                msg = "Successfully {} {} from {}".format("removed", itemName, tableName)
                self.send_message(msg)
                return msg, 200
            elif reminderBotRq[1].lower() == "show":

                idxToTableName = reminderBotRq.index("show") + 1
                tableName = ""
                for tableToAddName in reminderBotRq[idxToTableName:]:
                    tableName += tableToAddName
                    tableName += " "
                tableName = tableName.rstrip()

                conn = psycopg2.connect(database='devlpvf6ln40ak',
                                        user='liomjizjcckrtw',
                                        password='aa34a6b5ee9b3e0d8a945a4413d5479908a1d44cbc987a4f5060840c1d680412',
                                        host='ec2-107-22-169-45.compute-1.amazonaws.com',
                                        port='5432',
                                        sslmode='require')
                cur = conn.cursor()
                if tableName == "all":
                    query = sql.SQL("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
                else:
                    query = sql.SQL("SELECT item FROM {};") \
                        .format(sql.Identifier(tableName))

                cur.execute(query)
                tableItemContents = ""
                for table in cur.fetchall():
                    tableItemContents += table[0]
                    tableItemContents += ", "
                tableItemContents = tableItemContents.rstrip()

                self.send_message("{}: {}".format(tableName, tableItemContents))
                conn.commit()
                conn.close()
                return "{}: {}".format(tableName, tableItemContents), 200
            elif reminderBotRq[1].lower() == "help":
                commands = "weather: housebot/boy weather <city> " \
                           "\n add: housebot/boy add <item> to <list>" \
                           "\n rm: housebot/boy rm <item> from <list> " \
                           "\n\t if list is empty list is deleted" \
                           "\n show: housebot/boy show <list>" \
                           "\n\t housebot/boy show all (lists all lists already created)"

                msg = "Commands: {}".format(commands)
                self.send_message(msg)

            return "ok", 200
