# GWC-Shopping-App

Flask + SQLite shopping backend that accepts a location and item name, then returns
nearby store prices sorted by best final price after discount.

## Run

```bash
python app.py
```

The API will run on `http://127.0.0.1:5000`.

## API

### `POST /search`

Request body:

```json
{
  "location": "Orlando, FL",
  "item": "coca cola"
}
```

Response includes:
- geocoded coordinates for the user location
- nearby stores
- item prices
- discount calculation and final prices
- results sorted by lowest final price
