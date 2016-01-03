from app import app, database
from models import Entry, FTSEntry
import views


app.add_url_rule('/login/', 'login', views.login,  methods=['GET', 'POST'])
app.add_url_rule('/logout/',  'logout', views.logout,  methods=['GET', 'POST'])
app.add_url_rule('/', 'index', views.index)


def main():
    database.create_tables([Entry, FTSEntry], safe=True)
    app.run(debug=True)

if __name__ == '__main__':
    main()

