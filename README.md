# ShopScout

ShopScout helps you find nearby supermarkets for a shopping trip. The Vue
frontend sends the item and location to the Flask API; the current API returns
store locations, not product availability or prices.

## Run locally

1. Install the Python dependencies and configure Geoapify:

```sh
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root and add your Geoapify API key:

```text
GEOAPIFY_KEY=your_api_key
```

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
Open the local URL printed by Vite to use the app.

## Production build

Build the Vue frontend with:

```sh
npm run build
```

The development proxy is not included in the production build. Configure your
production web server to route `/search` to the Flask API.
