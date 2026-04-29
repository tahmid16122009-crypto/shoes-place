@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password")

        if password == "Tahmid1122":
            session["admin"] = True
            return redirect("/admin/dashboard")
        else:
            return "Wrong password"

    return render_template("admin_login.html")


@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    products = supabase.table("products").select("*").execute().data or []
    orders = supabase.table("orders").select("*").execute().data or []

    return render_template("admin.html", products=products, orders=orders)