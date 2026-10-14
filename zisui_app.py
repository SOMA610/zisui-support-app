from flask import Flask, request, url_for, render_template, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///zisui.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class MemoItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    recipe = db.Column(db.Text, nullable=False)
    food = db.Column(db.Text, nullable=False)
    easy = db.Column(db.Integer, nullable=False, default=5)
class ShoppingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    checked = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    keyword = request.args.get("keyword", "").strip() #検索機能
    sort = request.args.get("sort","title")           #並び替え機能
    query = MemoItem.query
    if keyword:
        query = query.filter(
            db.or_(
                MemoItem.title.contains(keyword),
                MemoItem.food.contains(keyword)
            )
        )
    if sort == "easy_asc":
        query = query.order_by(MemoItem.easy.asc())
    elif sort == "easy_desc":
        query = query.order_by(MemoItem.easy.desc())
    else:query = query.order_by(MemoItem.title.asc())

    items = query.all()
    return render_template("list.html", items=items,keyword=keyword)

@app.route("/memo/<int:id>", methods=["GET", "POST"])
def memo(id: int):
    it = MemoItem.query.get(id)
    if id == 0 or it is None:
        it = MemoItem(title="料理名", recipe="", food="", easy=5)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        recipe = request.form.get("recipe", "").strip()
        food = request.form.get("food", "").strip()
        easy = int(request.form.get("easy", 5))

        if title == "":
            return "料理名を入力してください"
        if recipe == "":
            return "レシピを入力してください"
        if food == "":
            return "食材を入力してください"
        if easy < 1 or easy > 5:
            return "難易度は1〜5で選択してください"

        it.title = title
        it.recipe = recipe
        it.food = food
        it.easy = easy

        if id == 0:
            db.session.add(it)
        db.session.commit()
        return redirect(url_for("index"))

    return render_template("zisui.html", it=it)


@app.route("/memo/<int:id>/delete",methods=["POST"])
def delete_memo(id: int):  #作成したメモの削除機能
    it = MemoItem.query.get(id)
    if it is None:
        return redirect(url_for("index"))
    db.session.delete(it)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/shopping/add/<int:id>", methods=["POST"])
def add_to_shopping(id: int):
    it = MemoItem.query.get(id)

    if it is None:
        return redirect(url_for("index"))

    for line in it.food.splitlines():

        line = line.strip()

        if line == "":
            continue

        if "：" in line:
            name = line.split("：", 1)[0].strip()
        else:
            name = line

        shopping_item = ShoppingItem(name=name)
        db.session.add(shopping_item)

    db.session.commit()

    return redirect(url_for("shopping"))

@app.route("/shopping/check/<int:id>", methods=["POST"])
def check_shopping(id: int):
    item = db.session.get(ShoppingItem, id)

    if item is not None:
        item.checked = not item.checked
        db.session.commit()

    return redirect(url_for("shopping"))

@app.route("/shopping/delete/<int:id>", methods=["POST"])
def delete_shopping(id: int):
    item = db.session.get(ShoppingItem, id)

    if item is not None:
        db.session.delete(item)
        db.session.commit()

    return redirect(url_for("shopping"))

@app.route("/shopping/clear", methods=["POST"])
def clear_shopping():
    ShoppingItem.query.delete()
    db.session.commit()

    return redirect(url_for("shopping"))

@app.route("/shopping")
def shopping():
    items = ShoppingItem.query.all()
    return render_template("shopping.html", items=items)

@app.route("/shopping/add-manual", methods=["POST"])
def add_shopping_manual():

    name = request.form.get("name", "").strip()

    if name == "":
        return redirect(url_for("shopping"))

    item = ShoppingItem(name=name, checked=False)

    db.session.add(item)
    db.session.commit()

    return redirect(url_for("shopping"))

if __name__ == "__main__":
    app.run(debug=True, port=8888)