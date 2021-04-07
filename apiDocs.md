<title>PlayList Length Service</title>
# PlayList Length Service

## Usage

**Definition**

- `Accepted Messages on localhost:9999 (POST)`

&nbsp;&nbsp;&nbsp;&nbsp;{<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"id": "PLAYLIST LINK / PLAYLIST ID",<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"user": "user name",<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"key": "user password"<br />
&nbsp;&nbsp;&nbsp;&nbsp;}


**Definition**

`POST /`

**Response**

- `200 OK` on success


&nbsp;&nbsp;&nbsp;&nbsp;{<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"message": "Success",<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"tempoIMP": "Un secondo.",<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"durata": "12 minuti.",<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"counter": 4<br />
&nbsp;&nbsp;&nbsp;&nbsp;}


**Definition**

`GET /`

**Response**

- `200 OK` on success, show this page


**Response Errors**

- `500 INTERNAL SERVER ERROR` on invalid request link


&nbsp;&nbsp;&nbsp;&nbsp;{<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"message": "errore id non corretto"<br />
&nbsp;&nbsp;&nbsp;&nbsp;}


- `403 FORBIDDEN` on invalid user name or password


&nbsp;&nbsp;&nbsp;&nbsp;{<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'message': 'errore user o key non validi'<br />
&nbsp;&nbsp;&nbsp;&nbsp;}