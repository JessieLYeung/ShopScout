# ShopScout

ShopScout finds supermarkets near a ZIP code and compares matching product
prices at supported retailers. It displays the store addresses and unit prices
to help shoppers compare options.

## Run locally

1. Install the Python dependencies:

```sh
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root and configure both API keys:

```text
GEOAPIFY_KEY=your_api_key
APIFY_TOKEN=your_api_token
```

Geoapify provides geocoding and nearby-store data. Apify runs the product-price
search. Keep these keys private and do not commit your `.env` file.

Start the backend in one terminal:

```sh
python app.py
```

Install the frontend dependencies and start Vite in another terminal:

```sh
npm install
npm run dev
```

Vite proxies `/search` requests to the Flask server at `http://127.0.0.1:5000`.
Open the local URL printed by Vite to use the app. Product price searches
currently support Publix, Aldi, and Sprouts when returned by the nearby-store
search.

## Production build

Build the Vue frontend with:

```sh
npm run build
```

The development proxy is not included in the production build. Configure your
production web server to route `/search` to the Flask API.
