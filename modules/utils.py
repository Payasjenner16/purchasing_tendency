import sqlite3
import pandas as pd
import random
from flask_mail import Mail, Message

mail = Mail()

df = pd.read_csv("static/data/dataset.csv")
data = pd.read_csv("static/data/ecommerce_behavior_dataset.csv")

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_db():
    conn=sqlite3.connect("purchasing_tendency.db", check_same_thread=False)
    conn.row_factory = dict_factory
    return conn

def generate_demand_alerts():

    df = pd.read_csv("static/data/ecommerce_dataset_fixed.csv")

    purchases = df[df["action"] == "purchase"]
    alerts = []

    demand = (
        purchases.groupby(["location","product_name"])
        .size()
        .reset_index(name="count")
    )

    for _, row in demand.iterrows():

        location = row["location"]
        product = row["product_name"]
        count = row["count"]

        if count >= 25:
            alerts.append({
                "type": "high",
                "message": f"High demand for {product} in {location}. Increase inventory."
            })

        elif count <= 5:
            alerts.append({
                "type": "low",
                "message": f"Low demand for {product} in {location}. Consider promotions."
            })

    # --------------------------------
    # RETURN ONLY ONE RANDOM ALERT
    # --------------------------------
    if alerts:
        return random.choice(alerts)

    return None

def generate_seller_alert():

    df = pd.read_csv("static/data/ecommerce_dataset_fixed.csv")

    purchases = df[df["action"] == "purchase"]
    alerts = []
    demand = (
        purchases.groupby(["location","product_name"])
        .size()
        .reset_index(name="count")
    )

    for _, row in demand.iterrows():

        location = row["location"]
        product = row["product_name"]
        count = row["count"]

        # 🚀 High demand
        if count >= 25:
            alerts.append({
                "type":"high",
                "icon":"🚀",
                "title":"High Demand Alert",
                "message":f"{product} demand is high in {location}. Increase stock."
            })

        # 📉 Low demand
        elif count <= 5:
            alerts.append({
                "type":"low",
                "icon":"📉",
                "title":"Low Demand Warning",
                "message":f"{product} demand is low in {location}. Consider promotion."
            })

        # 🔥 Trending
        elif 15 <= count < 25:
            alerts.append({
                "type":"trend",
                "icon":"🔥",
                "title":"Trending Product",
                "message":f"{product} is trending in {location}."
            })

        # 📍 Market opportunity
        elif count < 10:
            alerts.append({
                "type":"opportunity",
                "icon":"📍",
                "title":"Location Opportunity",
                "message":f"{product} may have potential demand in {location}."
            })

    if alerts:
        return random.choice(alerts)

    return None

def send_alert_email(email, alerts):

    if not alerts:
        return

    alert_text = ""
    for alert in alerts:
        alert_text += f"- {alert['message']}\n"

    msg = Message(
        subject="Demand Insight Alert",
        recipients=[email],
        body=f"""
Hello Seller,

Our system detected important demand insights:

{alert_text}

Please adjust your inventory accordingly.

Purchasing Intelligence System
"""
    )

    mail.send(msg)
