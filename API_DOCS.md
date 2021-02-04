# API Documentation

This is the documentation for all of the API routes served by this application.

## General Notes

The application will only accept JSON requests or multipart form data (files), all other requests will be rejected with a `400 Bad Request` response.

## `/mikerecords`: `GET`

Returns all MIKE Records in JSON as an array of objects.

### Example:

    <- GET /mikerecords

    -> OK
    [
        {
            "unRegion": "Africa",
            "subregionName": "Eastern Africa",
            "subregionId": "FE",
            "countryName": "Rwanda",
            "countryCode": "rw",
            "mikeSiteId": "AKG",
            "mikeSiteName": "Akagera",
            "year": 2014,
            "totalNumberOfCarcasses": 0,
            "numberOfIllegalCarcasses": 0
        },
        {
            "unRegion": "Africa",
            "subregionName": "Eastern Africa",
            "subregionId": "FE",
            "countryName": "Rwanda",
            "countryCode": "rw",
            "mikeSiteId": "AKG",
            "mikeSiteName": "Akagera",
            "year": 2013,
            "totalNumberOfCarcasses": 1,
            "numberOfIllegalCarcasses": 0
        },
        ...
    ]

## `/login`: `POST`

Either logs a user in or renews their security token.

### Logging In

The client `POST`'s a JSON object containing a `password` field. If the password is correct, the server will return a security token in a JSON object. If the password is incorrect, the server will respond with `401 Unauthorized`.

#### Example:

    <- POST /login
    {
        "password": "elephants"
    }

    -> OK
    {
        "token": "xxxxx.yyyyy.zzzzz"
    }

### Renewing Security Token

The client `POST`'s a JSON object containing a `token` field. If the token is valid, then the server will return a new valid security token.

A security token will be valid for 30 minutes. A client should renew its security token at least every 30 minutes.

#### Example:

    <- POST /login
    {
        "token": "xxxxx.yyyyy.zzzzz"
    }

    -> OK
    {
        "token": "aaaaa.bbbbb.ccccc"
    }

## Admin Note

All routes starting with `/admin` require that the client be logged in to use, otherwise the server will respond with 401 Unauthorized.

## `/admin/upload`: `POST`

Receives a CSV in the MIKE database format and adds the records to the database, replacing enteries with the same MIKE site ID and year with the records from the CSV. If the file is not a CSV or is in the wrong format for a MIKE record CSV, the server will return `400 Bad Request`.

### Example:

    <- POST /admin/upload
    Multipart Form Data: whatever.csv

    -> OK
    {
        "message": "Records uploaded"
    }

## `/admin/update`: `GET`

Retrieves the current MIKE database and adding all records to the application database.

### Example:

    <- GET /admin/update

    -> OK
    {
        "message": "Records updated directly from the MIKE database"
    }

## `/admin/edit`: `POST`

Edits updates the application database with changes listed in a JSON request containing three lists of MIKE records: `added`, `changed`, and `removed`. Regardless of the list, all records with the same primary keys (MIKE site ID and year) are replaced.

### Example:

    <- POST /admin/edit
    {
        "added": [
            {
                "unRegion": "Africa",
                "subregionName": "Eastern Africa",
                "subregionId": "FE",
                "countryName": "Rwanda",
                "countryCode": "rw",
                "mikeSiteId": "AKG",
                "mikeSiteName": "Akagera",
                "year": 2021,
                "totalNumberOfCarcasses": 0,
                "numberOfIllegalCarcasses": 0
            },
            ...
        ],
        "changed": [
            {
                "unRegion": "Africa",
                "subregionName": "Eastern Africa",
                "subregionId": "FE",
                "countryName": "Rwanda",
                "countryCode": "rw",
                "mikeSiteId": "AKG",
                "mikeSiteName": "Akagera",
                "year": 2013,
                "totalNumberOfCarcasses": 3,
                "numberOfIllegalCarcasses": 0
            },
            ...
        ],
        "removed": [
            {
                "unRegion": "Africa",
                "subregionName": "Eastern Africa",
                "subregionId": "FE",
                "countryName": "Rwanda",
                "countryCode": "rw",
                "mikeSiteId": "AKG",
                "mikeSiteName": "Akagera",
                "year": 2013,
                "totalNumberOfCarcasses": 1,
                "numberOfIllegalCarcasses": 0
            },
            ...
        ]
    }

    -> OK
    {
        "message": "Records edited"
    }
