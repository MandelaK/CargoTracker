# CargoTracker
This application allows users to send and track their parcels.


Endpoints

POST /users/register | Allow users to register their accounts
POST /users/login | Allow users to log in

POST /admin/branch | Allow admins to register new branches and agents

POST /parcels | Create a parcel booking
GET /parcels | Get all parcels for current user

GET /parcels/id | Get details about an individual parcel
PATCH /parcels/id | Update details about individual parcel
