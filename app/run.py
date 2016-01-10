from app import app, database
from models import Entry, FTSEntry
import views


app.add_url_rule('/login/', 'login', views.login, methods=['GET', 'POST'])
app.add_url_rule('/logout/',  'logout', views.logout, methods=['GET', 'POST'])
app.add_url_rule('/', 'index', views.index, methods=['GET'])
app.add_url_rule('/create', 'create', views.create, methods=['GET', 'POST'])
app.add_url_rule('/drafts', 'drafts', views.drafts, methods=['GET'])
app.add_url_rule('/<slug>', 'detail', views.detail, methods=['GET'])


def main():
    database.create_tables([Entry, FTSEntry], safe=True)
    app.run(debug=True)

if __name__ == '__main__':
    """Run the Flask blog

    Use command `python app/run.py`
    """
    main()

