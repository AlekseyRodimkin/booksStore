# import os
#
# # путь до текстов
# print(os.path.abspath(os.path.join(__file__, '../books_files')))
#
# # вернуть всех юзеров
# user = db.session.query(User).all()
# return render_template('private/box.html', data=user)
# <p>Your login is: {{ data }}</p>
#
# # получить id usera
# u_id = flask_login.current_user.id
#     return render_template('private/box.html', data=u_id)