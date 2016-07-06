from flask import current_app, Blueprint, render_template

core = Blueprint("core", __name__, url_prefix="/")

# homepage
@core.route('/')
def home():
    return render_template('core/index.html',
                           is_home=True)
