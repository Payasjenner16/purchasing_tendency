from flask import Blueprint, render_template, request, redirect, session
import numpy as np

from modules.utils import get_db, df
from modules.ai_helper import recommender

buyer_bp = Blueprint("buyer", __name__)

@buyer_bp.route("/sequential")
def buyer_recommendation():

    # total purchases per location and product
    data = df.groupby(["district","product"])["purchases"].sum().reset_index()

    # pick top product per district
    top = data.sort_values("purchases", ascending=False).groupby("district").head(1)
    locations = top["district"].tolist()
    products = top["product"].tolist()
    scores = top["purchases"].tolist()

    return render_template(
        "sequential_dashboard.html",
        locations=locations,
        products=products,
        scores=scores
    )
# DEMAND INSIGHT
# -----------------------------

@buyer_bp.route("/demand")
def demand():

    grouped = df.groupby(["product","district"])["purchases"].sum().reset_index()
    products = {}

    for product in grouped["product"].unique():
        data = grouped[grouped["product"] == product]
        locations = data["district"].tolist()
        values = data["purchases"].tolist()

        colors = []

        for v in values:
            if v < 10:
                colors.append("#ff4d4d")   # red
            elif v < 20:
                colors.append("#ffc107")   # yellow
            else:
                colors.append("#28a745")   # green

        products[product] = {
            "locations": locations,
            "values": values,
            "colors": colors
        }

    return render_template("demand_dashboard.html", products=products)

# ------------------------------------------------
# ADD PRODUCT
# ------------------------------------------------

@buyer_bp.route("/buyer_register",methods=["GET","POST"])
def buyer_register():

    if request.method=="POST":

        name=request.form["name"]
        email=request.form["email"]
        mobile=request.form["mobile"]
        location=request.form["location"]
        age=request.form["age"]
        gender=request.form["gender"]
        username=request.form["username"]
        password=request.form["password"]

        conn=get_db()
        cur=conn.cursor()

        cur.execute("""
        INSERT INTO buyers
        (name,email,mobile,location,age,gender,username,password)
        VALUES(?,?,?,?,?,?,?,?)
        """,(name,email,mobile,location,age,gender,username,password))

        conn.commit()

        return redirect("/buyer_login")

    return render_template("buyer_register.html")

# ------------------------------------------------
# BUYER LOGIN
# ------------------------------------------------

@buyer_bp.route("/buyer_login",methods=["GET","POST"])
def buyer_login():

    if request.method=="POST":

        username=request.form["username"]
        password=request.form["password"]

        conn=get_db()
        cur=conn.cursor()

        cur.execute("SELECT * FROM buyers WHERE username=? AND password=?",(username,password))
        buyer=cur.fetchone()

        if buyer:

            session["buyer"]=buyer["id"]

            return redirect("/buyer_dashboard")

    return render_template("buyer_login.html")



# ------------------------------------------------
# BUYER DASHBOARD
# ------------------------------------------------

@buyer_bp.route("/buyer_dashboard")
def buyer_dashboard():

    if "buyer" not in session:
        return redirect("/buyer_login")

    conn=get_db()
    cur=conn.cursor()

    cur.execute("SELECT * FROM products")
    products=cur.fetchall()

    return render_template("buyer_dashboard.html",products=products)



# ------------------------------------------------
# ADD TO CART
# ------------------------------------------------

@buyer_bp.route("/add_to_cart/<id>")
def add_to_cart(id):

    if "buyer" not in session:
        return redirect("/buyer_login")

    conn=get_db()
    cur=conn.cursor()

    cur.execute("""
    INSERT INTO cart(buyer_id,product_id)
    VALUES(?,?)
    """,(session["buyer"],id))

    cur.execute("""
    INSERT INTO interactions(user_id,product_id,action)
    VALUES(?,?,'cart')
    """,(session["buyer"],id))

    conn.commit()

    return redirect("/cart")

# ------------------------------------------------
# VIEW CART
# ------------------------------------------------

@buyer_bp.route("/cart")
def cart():

    if "buyer" not in session:
        return redirect("/buyer_login")

    conn=get_db()
    cur=conn.cursor()

    cur.execute("""
    SELECT cart.*,products.name,products.price,products.image
    FROM cart
    JOIN products ON products.id=cart.product_id
    WHERE buyer_id=?
    """,(session["buyer"],))

    items=cur.fetchall()

    return render_template("cart.html",items=items)

# ------------------------------------------------
# PLACE ORDER
# ------------------------------------------------

@buyer_bp.route("/place_order/<product_id>")
def place_order(product_id):

    if "buyer" not in session:
        return redirect("/buyer_login")

    conn=get_db()
    cur=conn.cursor()

    cur.execute("SELECT * FROM products WHERE id=?",(product_id,))
    product=cur.fetchone()

    cur.execute("""
    INSERT INTO orders(buyer_id,seller_id,product_id,price)
    VALUES(?,?,?,?)
    """,(session["buyer"],product["seller_id"],product_id,product["price"]))

    cur.execute("""
    INSERT INTO interactions(user_id,product_id,action)
    VALUES(?,?,'purchase')
    """,(session["buyer"],product_id))

    cur.execute("""
    DELETE FROM cart 
    WHERE buyer_id=? AND product_id=?
    """,(session["buyer"],product_id))

    conn.commit()

    return redirect("/buyer_orders")

# ------------------------------------------------
# BUYER ORDER HISTORY
# ------------------------------------------------

@buyer_bp.route("/buyer_orders")
def buyer_orders():

    conn=get_db()
    cur=conn.cursor()

    cur.execute("""
    SELECT orders.*,products.name,products.image
    FROM orders
    JOIN products ON products.id=orders.product_id
    WHERE buyer_id=?
    """,(session["buyer"],))

    orders=cur.fetchall()

    return render_template("buyer_orders.html",orders=orders)

# ------------------------------------------------
# PAYMENT
# ------------------------------------------------

@buyer_bp.route("/pay/<id>")
def pay(id):

    conn=get_db()
    cur=conn.cursor()

    cur.execute("UPDATE orders SET payment_status='paid' WHERE id=?",(id,))
    conn.commit()

    return redirect("/buyer_orders")

class Config:

    def __init__(self):

        self.embedding_size = 128
        self.sequence_length = 50
        self.community_clusters = 10
        self.recommendation_top_k = 5

# --------------------------------------------------------
# DATA COLLECTION MODULE
# --------------------------------------------------------

class DataCollector:

    def __init__(self):
        self.customer_data = []
        self.product_data = []
        self.transaction_data = []

    def load_data(self):

        for i in range(100):
            self.customer_data.append({
                "customer_id": i,
                "location": "region_" + str(i % 5)
            })

        for i in range(50):
            self.product_data.append({
                "product_id": i,
                "category": "category_" + str(i % 6)
            })

        for i in range(200):
            self.transaction_data.append({
                "customer_id": np.random.randint(0,100),
                "product_id": np.random.randint(0,50)
            })

# --------------------------------------------------------
# GRAPH CONSTRUCTION
# --------------------------------------------------------

class GraphBuilder:

    def build_graph(self, transactions):
        edges = []
        for t in transactions:
            edges.append((t["customer_id"], t["product_id"]))

        return edges

# --------------------------------------------------------
# TENDGRAPHNET MODEL (GNN)
# --------------------------------------------------------

class TendGraphNet:

    def __init__(self, config):

        self.config = config
        self.embeddings = {}

    def train(self, graph_edges):

        for edge in graph_edges:
            node = edge[0]

            if node not in self.embeddings:
                self.embeddings[node] = np.random.rand(self.config.embedding_size)

    def get_embedding(self, node):

        return self.embeddings.get(node, np.zeros(self.config.embedding_size))


# --------------------------------------------------------
# COMMUNITY DETECTION
# --------------------------------------------------------

class CommunityDiscovery:

    def detect(self, embeddings):
        communities = {}
        for node, emb in embeddings.items():
            community_id = int(np.sum(emb) % 5)
            communities[node] = community_id

        return communities

# --------------------------------------------------------
# SEQBEHNET MODEL (SASRec)
# --------------------------------------------------------

class SeqBehNet:

    def __init__(self, config):
        self.config = config

    def train_sequences(self, transactions):
        sequences = {}

        for t in transactions:

            user = t["customer_id"]
            if user not in sequences:
                sequences[user] = []

            sequences[user].append(t["product_id"])

        return sequences

    def predict_next(self, sequence):

        predictions = []
        for i in range(self.config.recommendation_top_k):
            predictions.append(np.random.randint(0,50))

        return predictions

# --------------------------------------------------------
# DEMAND ANALYSIS
# --------------------------------------------------------

class DemandInsight:

    def analyze(self, transactions):
        demand = {}
        for t in transactions:
            pid = t["product_id"]
            if pid not in demand:
                demand[pid] = 0
            demand[pid] += 1
        return demand

# --------------------------------------------------------
# RECOMMENDATION ENGINE
# --------------------------------------------------------

class RecommendationEngine:

    def generate(self, community, seq_predictions):
        recommendations = []
        for p in seq_predictions:
            recommendations.append(p)
        return recommendations

# --------------------------------------------------------
# MAIN ANALYTICS PIPELINE
# --------------------------------------------------------

class PurchasingTendencyPipeline:

    def __init__(self):

        self.config = Config()

        self.collector = DataCollector()
        self.graph_builder = GraphBuilder()

        self.tend_graph = TendGraphNet(self.config)
        self.community_model = CommunityDiscovery()

        self.seq_model = SeqBehNet(self.config)
        self.demand_model = DemandInsight()

        self.recommender = RecommendationEngine()

    def run(self):

        self.collector.load_data()

        edges = self.graph_builder.build_graph(self.collector.transaction_data)

        self.tend_graph.train(edges)

        communities = self.community_model.detect(self.tend_graph.embeddings)
        sequences = self.seq_model.train_sequences(self.collector.transaction_data)
        demand = self.demand_model.analyze(self.collector.transaction_data)

        sample_user = 1

        seq_predictions = self.seq_model.predict_next(sequences.get(sample_user, []))
        community = communities.get(sample_user, 0)
        recommendations = self.recommender.generate(community, seq_predictions)

        result = {
            "user": sample_user,
            "community": community,
            "recommendations": recommendations
        }

        return result

# ------------------------------------------------
# AI RECOMMENDATIONS + MULTI-SHOP MAP
# ------------------------------------------------

@buyer_bp.route("/recommendations")
def recommendations():

    if "buyer" not in session:
        return redirect("/buyer_login")

    conn = get_db()
    cur = conn.cursor()

    buyer_id = session["buyer"]

    # Step 1: Use GNN model to get list of recommended product IDs ordered by similarity
    recommended_ids = recommender.get_gnn_recommendations(buyer_id)

    if not recommended_ids:
        return render_template("recommendations.html", products=[])

    # Step 2: Fetch products from database that exist in GNN recommendations
    # Fetch details for the first 5 products from GNN that exist in SQLite
    format_strings = ','.join(['?'] * len(recommended_ids))

    query = f"""
        SELECT 
            products.id,
            products.name,
            products.price,
            products.image,
            products.specification,

            sellers.shopname,
            sellers.address,
            sellers.latitude,
            sellers.longitude

        FROM products
        JOIN sellers ON sellers.id = products.seller_id

        WHERE products.id IN ({format_strings})
    """

    cur.execute(query, tuple(recommended_ids))
    all_recs = cur.fetchall()

    # Order the retrieved products according to the GNN rank list
    recs_map = {r["id"]: r for r in all_recs}
    recs = []
    for pid in recommended_ids:
        if pid in recs_map:
            recs.append(recs_map[pid])
            if len(recs) == 5:
                break

    return render_template("recommendations.html", products=recs)

@buyer_bp.route("/seq")
def seq():

    if "buyer" not in session:
        return redirect("/buyer_login")

    conn = get_db()
    cur = conn.cursor()

    buyer_id = session["buyer"]

    # --------------------------------
    # BUYER PURCHASE HISTORY
    # --------------------------------
    cur.execute("""
        SELECT products.id, products.name
        FROM orders
        JOIN products ON products.id = orders.product_id
        WHERE orders.buyer_id=?
        ORDER BY orders.id ASC
    """, (buyer_id,))

    history = cur.fetchall()
    purchased_products = [h["name"] for h in history]

    # Map purchase history database IDs
    purchase_history_pids = [h["id"] for h in history]

    # Get SASRec predictions
    predicted_pids = recommender.get_seq_recommendations(buyer_id, purchase_history_pids)

    # Fetch predicted product details
    dl_products = []
    if predicted_pids:
        format_strings = ','.join(['?'] * len(predicted_pids))
        cur.execute(f"""
            SELECT id, name, price, image, seller_id
            FROM products
            WHERE id IN ({format_strings})
        """, tuple(predicted_pids))
        all_dl_products = cur.fetchall()
        
        # Order by SASRec rank
        dl_map = {p["id"]: p for p in all_dl_products}
        for pid in predicted_pids:
            if pid in dl_map:
                dl_products.append(dl_map[pid])
                if len(dl_products) == 6:
                    break

    # --------------------------------
    # RULE-BASED ACCESSORIES RECOMMENDATIONS
    # --------------------------------
    products = []
    if history:
        # Check accessories based on last purchased product
        last_product = history[-1]
        product_name = last_product["name"].lower()
        product_id = last_product["id"]

        accessories = []
        if "mobile" in product_name or "phone" in product_name:
            accessories = ["case", "cover", "charger", "headphone", "earphone", "cable"]
        elif "laptop" in product_name or "macbook" in product_name:
            accessories = ["mouse", "keyboard", "bag", "cooling", "adapter"]
        elif "camera" in product_name:
            accessories = ["tripod", "lens", "memory", "card", "bag"]

        if accessories:
            cur.execute("SELECT id, name, price, image, seller_id FROM products")
            all_products = cur.fetchall()

            for p in all_products:
                pname = p["name"].lower()
                if p["id"] == product_id:
                    continue

                for word in accessories:
                    if word in pname:
                        products.append(p)
                        break

        products = products[:6]

    conn.close()

    return render_template(
        "seq.html",
        purchased_products=purchased_products,
        dl_products=dl_products,
        products=products
    )

@buyer_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
