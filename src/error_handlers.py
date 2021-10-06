from flask import render_template, Blueprint

blueprint = Blueprint("error_handlers", __name__)


@blueprint.app_errorhandler(400)
def page_not_found_400(e):
    return render_template("400.html"), 400


@blueprint.app_errorhandler(500)
def page_not_found_400(e):
    return render_template("500.html"), 500


@blueprint.app_errorhandler(404)
def page_not_found_404(e):
    return render_template("404.html"), 404
