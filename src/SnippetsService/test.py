import mysql.connector


if __name__ == '__main__':

    con = mysql.connector.connect(host='127.0.0.1', port=3306, username='identity', password='dev', database='idserver')

    # 69195

    for i in range(69195):
        query = "INSERT INTO user_claims (user_id, )"