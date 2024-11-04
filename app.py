from flask import (
    Flask,
    render_template,
    redirect,
    request,
    url_for,
    send_from_directory,
)
from db import get_db_connection
import os

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("home"))


@app.route("/home", methods=["GET"])
def home():
    return render_template("home.html", active_page="home")


@app.route("/posts", methods=["GET"])
def get_all_post():
    conn = get_db_connection()
    posts = conn.execute("SELECT * FROM post").fetchall()
    conn.close()
    # Se captura el mensaje de éxito si es que existe
    success_msg = request.args.get("success_msg")
    return render_template(
        "post/posts.html", posts=posts, active_page="posts", success_msg=success_msg
    )


@app.route("/post/<int:post_id>", methods=["GET"])
def get_one_post(post_id):
    conn = get_db_connection()
    post = conn.execute("SELECT * FROM post WHERE id = ?", (post_id,)).fetchone()
    conn.close()
    # Se valida que exista el Post
    if post is None:
        return redirect(url_for("get_all_post"))
    return render_template("post/post.html", post=post)


@app.route("/post/create", methods=["GET", "POST"])
def create_one_post():
    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()
        # Se valida el título y el contenido
        if not title or not content:
            error_msg = "Por favor, ingrese un " + (
                "título y un contenido."
                if not title and not content
                else "título." if not title else "contenido."
            )
            return render_template(
                "/post/create.html",
                title=title,
                content=content,
                error_msg=error_msg,
            )

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO post (title, content) VALUES (?, ?)", (title, content)
        )
        conn.commit()
        conn.close()
        return redirect(
            url_for("get_all_post", success_msg="Se ha creado el Post exitosamente.")
        )

    return render_template("post/create.html")


@app.route("/post/edit/<int:post_id>", methods=["GET", "POST"])
def edit_one_post(post_id):
    conn = get_db_connection()
    post = conn.execute("SELECT * FROM post WHERE id = ?", (post_id,)).fetchone()
    conn.close()
    # Se valida que exista el Post
    if post is None:
        return redirect(url_for("get_all_post"))

    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()
        # Se valida el título y el contenido
        if not title or not content:
            error_msg = "Por favor, ingrese un " + (
                "título y un contenido."
                if not title and not content
                else "título." if not title else "contenido."
            )
            return render_template("post/edit.html", post=post, error_msg=error_msg)

        conn = get_db_connection()
        conn.execute(
            "UPDATE post SET title = ?, content = ? WHERE id = ?",
            (title, content, post_id),
        )
        conn.commit()
        conn.close()
        return redirect(
            url_for(
                "get_all_post", success_msg="Se ha actualizado el Post exitosamente."
            )
        )

    elif request.method == "GET":
        return render_template("post/edit.html", post=post)


@app.route("/post/delete/<int:post_id>", methods=["POST"])
def delete_one_post(post_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM post WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    return redirect(
        url_for("get_all_post", success_msg="Se ha eliminado el Post exitosamente.")
    )


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


if __name__ == "__main__":
    app.run(debug=True, port=80)
