from flask import Blueprint, render_template, request, redirect, session, current_app
from flask_mail import Message
import pandas as pd
import random
import os

from modules.utils import get_db, df, data, mail, generate_seller_alert

seller_bp = Blueprint("seller", __name__)

@seller_bp.route("/seller_register",methods=["GET","POST"])
def seller_register():

    if request.method=="POST":

        name=request.form["name"]
        email=request.form["email"]
        mobile=request.form["mobile"]
        shopname=request.form["shopname"]
        address=request.form["address"]
        category=request.form["category"]
        lat=request.form["latitude"]
        lon=request.form["longitude"]
        username=request.form["username"]
        password=request.form["password"]

        conn=get_db()
        cur=conn.cursor()

        sql="""INSERT INTO sellers
        (name,email,mobile,shopname,address,category,latitude,longitude,username,password)
        VALUES(?,?,?,?,?,?,?,?,?,?)"""

        cur.execute(sql,(name,email,mobile,shopname,address,category,lat,lon,username,password))
        conn.commit()

        return redirect("/seller_login")

    return render_template("seller_register.html")

# ------------------------------------------------
# SELLER LOGIN
# ------------------------------------------------

@seller_bp.route("/seller_login",methods=["GET","POST"])
def seller_login():

    if request.method=="POST":

        username=request.form["username"]
        password=request.form["password"]

        conn=get_db()
        cur=conn.cursor()

        cur.execute("SELECT * FROM sellers WHERE username=? AND password=?",(username,password))
        seller=cur.fetchone()

        if seller:
            session["seller"]=seller["id"]

            return redirect("/seller_dashboard")

    return render_template("seller_login.html")

@seller_bp.route("/seller_dash")
def dash():
    import pandas as pd
    import random

    df = pd.read_csv("static/data/ecommerce_dataset_fixed.csv")
    purchases = df[df["action"] == "purchase"]

    # --------------------------------
    # Total demand per location
    # --------------------------------
    location_totals = (
        purchases.groupby("location")
        .size()
        .reset_index(name="total_demand")
    )

    # --------------------------------
    # Product demand per location
    # --------------------------------
    location_products = (
        purchases.groupby(["location", "product_name"])
        .size()
        .reset_index(name="count")
    )

    # --------------------------------
    # Coordinates
    # --------------------------------
    coordinates = {
        "Chennai": (13.0827, 80.2707),
        "Delhi": (28.7041, 77.1025),
        "Mumbai": (19.0760, 72.8777),
        "Bangalore": (12.9716, 77.5946),
        "Hyderabad": (17.3850, 78.4867),
        "Pune": (18.5204, 73.8567),
        "Kolkata": (22.5726, 88.3639),
        "Madurai": (9.9252, 78.1198),
        "Coimbatore": (11.0168, 76.9558),
        "Trichy": (10.7905, 78.7047)
    }

    # --------------------------------
    # Demand thresholds
    # --------------------------------
    min_val = location_totals["total_demand"].min()
    max_val = location_totals["total_demand"].max()

    medium_threshold = min_val + (max_val - min_val) * 0.4
    high_threshold = min_val + (max_val - min_val) * 0.7

    # --------------------------------
    # Map points
    # --------------------------------
    map_data = []

    for _, row in location_products.iterrows():

        loc = row["location"]
        product = row["product_name"]
        demand = row["count"]

        if loc not in coordinates:
            continue

        total_loc_demand = int(
            location_totals[location_totals["location"] == loc]["total_demand"].values[0]
        )

        # demand level by location total
        if total_loc_demand <= medium_threshold:
            level = "low"
        elif total_loc_demand <= high_threshold:
            level = "medium"
        else:
            level = "high"

        lat, lng = coordinates[loc]

        # offset so markers don't overlap
        lat += random.uniform(-0.04, 0.04)
        lng += random.uniform(-0.04, 0.04)

        map_data.append({
            "name": loc,
            "lat": lat,
            "lng": lng,
            "product": product,
            "demand": int(demand),
            "level": level
        })

    # --------------------------------
    # Top products list for cards
    # --------------------------------
    location_data = {}

    for loc in location_products["location"].unique():

        loc_df = location_products[location_products["location"] == loc]
        top = loc_df.sort_values("count", ascending=False).head(5)
        location_data[loc] = {
            "products": top["product_name"].tolist(),
            "counts": top["count"].tolist()
        }

    return render_template(
        "dash.html",
        map_data=map_data,
        location_data=location_data
    )
@seller_bp.route("/analytics")

def analytics():

    import pandas as pd

    df = pd.read_csv("static/data/ecommerce_dataset_fixed.csv")

    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%d-%m-%y")
    purchases = df[df["action"] == "purchase"]

    # Top selling products
    product_popularity = (
        purchases.groupby("product_name")
        .size()
        .sort_values(ascending=False)
        .head(8)
    )

    # Demand by location
    location_demand = purchases.groupby("location").size()

    # Category demand
    category_demand = purchases.groupby("category").size()

    # Monthly sales trend
    sales_trend = purchases.groupby(purchases["timestamp"].dt.month).size()

    return render_template(
        "analytics.html",

        products=product_popularity.index.tolist(),
        product_counts=product_popularity.values.tolist(),

        locations=location_demand.index.tolist(),
        location_counts=location_demand.values.tolist(),

        categories=category_demand.index.tolist(),
        category_counts=category_demand.values.tolist(),

        months=sales_trend.index.tolist(),
        sales=sales_trend.values.tolist()
    )

# -------------------------------------------------
# DEMAND INSIGHT ALERT ENGINE
# -------------------------------------------------

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
    
@seller_bp.route("/seller_dashboard")
def seller_dashboard():

    if "seller" not in session:
        return redirect("/seller_login")

    alert = generate_seller_alert()

    return render_template(
        "seller_dashboard.html",
        alert=alert
    )

@seller_bp.route("/community")
def community():

    df["interaction"] = df["views"] + df["carts"] + df["purchases"]

    grouped = df.groupby("district").agg({
        "views":"sum",
        "carts":"sum",
        "purchases":"sum"
    }).reset_index()

    districts = grouped["district"].tolist()
    views = grouped["views"].tolist()
    carts = grouped["carts"].tolist()
    purchases = grouped["purchases"].tolist()

    return render_template(
        "community_dashboard.html",
        districts=districts,
        views=views,
        carts=carts,
        purchases=purchases
    )

# -----------------------------
# SEQUENTIAL BEHAVIOR
# -----------------------------

@seller_bp.route("/add_product",methods=["GET","POST"])
def add_product():

    if "seller" not in session:
        return redirect("/seller_login")

    if request.method=="POST":

        name=request.form["name"]
        price=request.form["price"]
        specification=request.form["specification"]

        file=request.files["image"]

        filename=file.filename
        filepath=os.path.join(current_app.config["UPLOAD_FOLDER"],filename)
        file.save(filepath)

        conn=get_db()
        cur=conn.cursor()

        cur.execute("""
        INSERT INTO products
        (seller_id,name,price,specification,image)
        VALUES(?,?,?,?,?)
        """,(session["seller"],name,price,specification,filename))

        conn.commit()

        return redirect("/view_products")

    return render_template("add_product.html")

@seller_bp.route("/view_products")
def view_products():

    if "seller" not in session:
        return redirect("/seller_login")

    conn=get_db()
    cur=conn.cursor()

    cur.execute("SELECT * FROM products WHERE seller_id=?",(session["seller"],))
    products=cur.fetchall()

    return render_template("view_products.html",products=products)

# ------------------------------------------------
# SELLER VIEW ORDERS
# ------------------------------------------------

@seller_bp.route("/seller_orders")
def seller_orders():

    if "seller" not in session:
        return redirect("/seller_login")

    conn=get_db()
    cur=conn.cursor()

    cur.execute("""
    SELECT orders.*,products.name, buyers.name AS buyer
    FROM orders
    JOIN products ON products.id=orders.product_id
    JOIN buyers ON buyers.id=orders.buyer_id
    WHERE orders.seller_id=?
    """,(session["seller"],))

    orders=cur.fetchall()

    return render_template("seller_orders.html",orders=orders)

@seller_bp.route("/approve_order/<id>")
def approve_order(id):

    conn=get_db()
    cur=conn.cursor()

    cur.execute("UPDATE orders SET status='approved' WHERE id=?",(id,))
    conn.commit()

    return redirect("/seller_orders")

@seller_bp.route("/reject_order/<id>")
def reject_order(id):

    conn=get_db()
    cur=conn.cursor()

    cur.execute("UPDATE orders SET status='rejected' WHERE id=?",(id,))
    conn.commit()

    return redirect("/seller_orders")

# ------------------------------------------------
# SELLER ANALYTICS
# ------------------------------------------------

@seller_bp.route("/seller_analytics")
def seller_analytics():

    if "seller" not in session:
        return redirect("/seller_login")

    conn = get_db()
    cur = conn.cursor()

    seller_id = session["seller"]

    # -----------------------------------
    # MY PRODUCT SALES
    # -----------------------------------

    cur.execute("""
    SELECT products.name, COUNT(orders.id) AS sales
    FROM orders
    JOIN products ON products.id = orders.product_id
    WHERE products.seller_id=?
    GROUP BY products.name
    """,(seller_id,))

    my_sales = cur.fetchall()


    # -----------------------------------
    # MY PRODUCT DEMAND
    # -----------------------------------

    cur.execute("""
    SELECT products.name, COUNT(interactions.product_id) AS demand
    FROM interactions
    JOIN products ON products.id = interactions.product_id
    WHERE products.seller_id=?
    GROUP BY products.name
    """,(seller_id,))

    my_demand = cur.fetchall()


    # -----------------------------------
    # MARKET TRENDING PRODUCTS
    # -----------------------------------

    cur.execute("""
    SELECT products.name, COUNT(interactions.product_id) AS demand
    FROM interactions
    JOIN products ON products.id = interactions.product_id
    WHERE products.seller_id != ?
    GROUP BY products.name
    ORDER BY demand DESC
    LIMIT 5
    """,(seller_id,))

    market_trending = cur.fetchall()


    # -----------------------------------
    # LOCATION BASED MARKET TREND
    # -----------------------------------

    cur.execute("""
    SELECT buyers.location, COUNT(orders.id) AS demand
    FROM orders
    JOIN buyers ON buyers.id = orders.buyer_id
    JOIN products ON products.id = orders.product_id
    GROUP BY buyers.location
    ORDER BY demand DESC
    """)

    location_trend = cur.fetchall()


    # -----------------------------------
    # PRODUCT LOCATION DEMAND
    # -----------------------------------

    cur.execute("""
    SELECT 
    products.name AS product,
    buyers.location,
    COUNT(orders.id) AS demand
    FROM products
    JOIN orders ON products.id = orders.product_id
    JOIN buyers ON buyers.id = orders.buyer_id
    WHERE products.seller_id=?
    GROUP BY products.name, buyers.location
    ORDER BY products.name, demand DESC
    """,(seller_id,))

    product_location = cur.fetchall()


    return render_template(
        "seller_analytics.html",
        my_sales=my_sales,
        my_demand=my_demand,
        market_trending=market_trending,
        location_trend=location_trend,
        product_location=product_location
    )
# ------------------------------------------------
# BUYER REGISTER
# ------------------------------------------------

@seller_bp.route("/community2")
def community2():

    conn = get_db()
    cur = conn.cursor()

    # --------------------------------
    # GET REAL PURCHASE DATA
    # --------------------------------
    cur.execute("""
        SELECT 
        buyers.location AS Location,
        sellers.category AS Product_Category,
        products.name AS Product_Name
        FROM orders
        JOIN buyers ON buyers.id = orders.buyer_id
        JOIN products ON products.id = orders.product_id
        JOIN sellers ON sellers.id = products.seller_id
    """)

    orders = cur.fetchall()

    conn.close()

    # --------------------------------
    # CONVERT ORDERS TO DATAFRAME
    # --------------------------------
    if orders:
        orders_df = pd.DataFrame(orders)

        # Add fake community label for new data
        orders_df["Community"] = "Live Buyers"

        # Merge dataset + live data
        combined = pd.concat([data, orders_df], ignore_index=True)

    else:
        combined = data.copy()

    # --------------------------------
    # COMMUNITY DISTRIBUTION
    # --------------------------------
    community = combined.groupby("Community").size()

    community_labels = list(community.index)
    community_values = list(community.values)

    # --------------------------------
    # PRODUCT CATEGORY DEMAND
    # --------------------------------
    category = combined.groupby("Product_Category").size()

    category_labels = list(category.index)
    category_values = list(category.values)

    # --------------------------------
    # LOCATION DEMAND
    # --------------------------------
    location = combined.groupby("Location").size()

    location_labels = list(location.index)
    location_values = list(location.values)

    # --------------------------------
    # PRODUCT POPULARITY
    # --------------------------------
    product = (
        combined.groupby("Product_Name")
        .size()
        .sort_values(ascending=False)
        .head(10)
    )

    product_labels = list(product.index)
    product_values = list(product.values)

    return render_template(
        "community2.html",
        community_labels=community_labels,
        community_values=community_values,
        category_labels=category_labels,
        category_values=category_values,
        location_labels=location_labels,
        location_values=location_values,
        product_labels=product_labels,
        product_values=product_values
    )

