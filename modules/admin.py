from flask import Blueprint, render_template, request, redirect, session
from modules.utils import get_db

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin",methods=["GET","POST"])
def admin():

    if request.method=="POST":

        username=request.form["username"]
        password=request.form["password"]

        if username=="admin" and password=="admin":
            session["admin"]="admin"
            return redirect("/admin_dashboard")

    return render_template("admin_login.html")


@admin_bp.route("/admin_dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect("/admin")

    conn=get_db()
    cur=conn.cursor()

    cur.execute("SELECT * FROM sellers")
    sellers=cur.fetchall()

    cur.execute("SELECT * FROM buyers")
    buyers=cur.fetchall()

    return render_template("admin_dashboard.html",sellers=sellers,buyers=buyers)

@admin_bp.route("/admin_analytics")
def admin_analytics():

    if "admin" not in session:
        return redirect("/admin")

    conn=get_db()
    cur=conn.cursor()

    # Calculate interaction score for products
    cur.execute("""
    SELECT products.id,
           products.name,
           COUNT(interactions.product_id) AS score
    FROM interactions
    JOIN products ON products.id = interactions.product_id
    GROUP BY interactions.product_id
    ORDER BY score DESC
    """)

    products=cur.fetchall()

    return render_template("admin_analytics.html",products=products)

@admin_bp.route("/remove_seller/<id>")
def remove_seller(id):

    conn=get_db()
    cur=conn.cursor()

    cur.execute("DELETE FROM sellers WHERE id=?",(id,))
    conn.commit()

    return redirect("/admin_dashboard")
