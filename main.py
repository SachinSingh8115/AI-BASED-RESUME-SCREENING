import mysql.connector
connection = mysql.connector.connect(host="localhost",
                                     user="root",
                                     password="Sachin@123",
                                     database="resume_screening"
 )
if connection.is_connected():
    print("MYSQL Database Connected Successfully!")
    connection.close()