# CargoTracker
This application allows users to send and track their parcels.

Backend API - https://cargotracker.herokuapp.com/

Endpoints

*All endpoints are prefixed with api/*

POST /auth/register | Allow users to register their accounts
POST /auth/agent | Superusers can use this to create new agents
POST /auth/login | Allow users to log in

POST /branch | Admin can use this to create a new branch

POST /cargo | Create a parcel booking
GET /cargo | Get all parcels for current user/agent
PATCH /cargo/<id> | Update details of current cargo

POST /orders | Create a single order
GET /orders/<tracking_id> | Get a single order
PATCH /orders/<tracking_id> | Update a single order


Using those endpoints, users can create cargo and branch admins can book the cargo and track the status of the order. All endpoints are rightfully secured, so users ony get access to data they are allowed to.

You can create an admin user by running the following command from the root directory:

```
python cargotracker/manage.py runscript --script-args email="admin@cargotracker.com"
```

All such admins have a default password of `adminpassword`.

The API is deployed on Heroku: https://cargotracker.herokuapp.com/
