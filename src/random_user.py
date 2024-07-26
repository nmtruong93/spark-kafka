import os.path

import requests
import sqlite3
from config.config import settings
from config.log_config import logger


def crawl_data():
    """
    Get data from randomuser.me
    :return: dict
    """
    url = "https://randomuser.me/api/"
    response = requests.get(url)
    return response.json()


def clean_data(data):
    """
    Clean data from crawl_data

    :param data: dict
    :return: dict
    """
    user_info = data['results'][0]
    full_name = f"{user_info['name']['first']} {user_info['name']['last']}"
    gender = user_info['gender']
    street = str(user_info['location']['street']['number']) + ' ' + user_info['location']['street']['name'] + ', ' + user_info['location']['city']
    state = user_info['location']['state']
    country = user_info['location']['country']
    timezone = user_info['location']['timezone']['offset']
    email = user_info['email']
    dob = user_info['dob']['date']
    age = user_info['dob']['age']
    phone = user_info['phone']
    cell = user_info['cell']
    return {
        "full_name": full_name,
        "gender": gender,
        "street": street,
        "state": state,
        "country": country,
        "timezone": timezone,
        "email": email,
        "dob": dob,
        "age": age,
        "phone": phone,
        "cell": cell
    }


def load_to_sql(cleaned_dict):
    """
    Load data to SQLite

    :param cleaned_dict: dict
    :return: None
    """
    try:
        conn = sqlite3.connect(os.path.join(settings.BASE_DIR, 'user.db'))
        cursor = conn.cursor()
        # Create table users if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name VARCHAR(255),
                gender VARCHAR(50),
                street VARCHAR(255),
                state VARCHAR(255),
                country VARCHAR(255),
                timezone VARCHAR(50),
                email VARCHAR(255),
                dob VARCHAR(50),
                age INTEGER,
                phone VARCHAR(50),
                cell VARCHAR(50)
            );
        """)
        conn.commit()

        # Insert data to table users
        sql = """
            INSERT INTO users(
                full_name,
                gender,
                street,
                state,
                country,
                timezone,
                email,
                dob,
                age,
                phone,
                cell
            )
            VALUES (
                :full_name,
                :gender, 
                :street,
                :country,
                :state,
                :timezone,
                :email,
                :dob,
                :age,
                :phone,
                :cell
             );
        """
        cursor.execute(sql, cleaned_dict)
        conn.commit()

        cursor.close()
        conn.close()
        logger.info("Data loaded successfully!")
    except Exception as e:
        logger.info(f"Error: {e}")


if __name__ == '__main__':
    data = crawl_data()
    cleaned = clean_data(data)
    load_to_sql(cleaned)
    print("DONE")
