from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from door_lock_db import DoorLockDB

app = Flask(__name__)
api = Api(app)

db = DoorLockDB()

# def abort_if_user_doesnt_exist(user):
#     if user not in :
#         abort(404, message="Todo {} doesn't exist".format(todo_id))

parser = reqparse.RequestParser()
parser.add_argument('name')
parser.add_argument('pin')
parser.add_argument('rfid_code')
parser.add_argument('data')
parser.add_argument('image')
parser.add_argument('query', default=None)


# Todo
# shows a single todo item and lets you delete a todo item
# class User(Resource):
#     def get(self, user_id):
#         args = parser.parse_args()
#         name = {'name' : args['name']}
#         print(name)
#         item = db.get_to_db('alist', query=name)
#         # abort_if_todo_doesnt_exist(todo_id)
#         return item

    # def delete(self, todo_id):
    #     # abort_if_todo_doesnt_exist(todo_id)
    #     del TODOS[todo_id]
    #     return '', 204

    # def put(self, todo_id):
    #     args = parser.parse_args()
    #     name = {'name': args['name']}
    #     TODOS[todo_id] = task
    #     return task, 201


# # TodoList
# # shows a list of all todos, and lets you POST to add new tasks
class User(Resource):
    global db

    def get(self):
        args = parser.parse_args()
        items = db.get_to_db('alist', args['query'])
        return items

class UserList(Resource):
    global db

    def get(self):
        items = db.get_to_db('alist')
        return items

    def post(self):
        payload = {}
        args = parser.parse_args()
        payload['name'] = args['name']
        payload['pin'] = args['pin']
        payload['rfid_code'] = args['rfid_code']
        if args['image']:
            payload['image'] = args['image']
        # print(payload)
        post_doc = db.post_new_doc('alist', payload)

        return post_doc, 201
    
    def put(self):
        """
        This function is for a RESTful PUT into the database. This function is expecting a JSON object structured like following:
        {
            "name" : <user name>,
            "data" : {
                "name" : <new name>
                "image" : <image id>
            }
        }
        The name is used to query the DB for a user to retrieve their Object ID. Then, the object ID is used for the PUT request.
        The data object contains the necessary fields and updated values 
        """
        payload = {}
        args = parser.parse_args()
        payload['name'] = args['name']
        raw_data = args['data']
        # print(raw_data)
        user_info = db.get_to_db('alist', query=payload)
        # print(user_info)
        user_info = user_info[0]
        user_id = user_info.get('_id')
        print(user_id)
        updated_doc = db.update_doc('alist', object_id=user_id, payload=raw_data)
        
        return updated_doc, 202


        # response = requests.request("PUT", url, data=payload, headers=headers)        

##
## Actually setup the Api resource routing here
##
api.add_resource(UserList, '/users')
api.add_resource(User, '/user')


if __name__ == '__main__':
    app.run(debug=True)

