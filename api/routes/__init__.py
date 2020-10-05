## Author : Kharizuno
## Github : https://github.com/kharizuno

from api.controllers import userCtrl

def apiRoutes(app):

    # User Route
    app.add_resource(userCtrl.UserAll, '/user') # GET
    app.add_resource(userCtrl.UserGet, '/user/<idx>')  # GET WITH ID
    app.add_resource(userCtrl.UserRegister, '/user/register')  # POST
    app.add_resource(userCtrl.UserCreate, '/user')  # POST
    app.add_resource(userCtrl.UserUpdate, '/user/<idx>')  # PUT
    app.add_resource(userCtrl.UserDelete, '/user/<idx>')  # DELETE

    return app