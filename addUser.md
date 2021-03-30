<title>PlayList Length Service</title>
# PlayList Length Service

## Adding a User
- `Accepted Messages on localhost:9999/addUser (POST)`

&nbsp;&nbsp;&nbsp;&nbsp;{<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"username": "user name",<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"password": "user password"<br />
&nbsp;&nbsp;&nbsp;&nbsp;}

**Definition**

`POST /`

**Response**

- `200 OK` on success


&nbsp;&nbsp;&nbsp;&nbsp;{<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"message": "success, user added.",<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"user": "username - password"<br />
&nbsp;&nbsp;&nbsp;&nbsp;}

**Response Errors**

- `500 INTERNAL SERVER ERROR` on internal error writing the json


&nbsp;&nbsp;&nbsp;&nbsp;{<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'message': 'error'<br />
&nbsp;&nbsp;&nbsp;&nbsp;}


- `500 INTERNAL SERVER ERROR` on user already in the json


&nbsp;&nbsp;&nbsp;&nbsp;{<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'message': 'user already there'<br />
&nbsp;&nbsp;&nbsp;&nbsp;}