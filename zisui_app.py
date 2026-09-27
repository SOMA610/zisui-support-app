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

if __name__ == "__main__":
    app.run(debug=True, port=8888)