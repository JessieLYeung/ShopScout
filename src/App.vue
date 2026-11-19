<script setup>
import { computed, ref } from 'vue'

const product = ref('')
const location = ref('')
const loading = ref(false)
const error = ref('')
const stores = ref(null)
const productGroups = ref(null)
const searchedProduct = ref('')
const searchedLocation = ref('')

const productTypes = [
  { key: 'volume', label: 'Volume', unit: 'fl oz' },
  { key: 'weight', label: 'Weight', unit: 'oz' },
  { key: 'count', label: 'Count', unit: 'item' },
]

const products = computed(() =>
  productGroups.value
    ? productTypes.flatMap(({ key }) => productGroups.value[key])
    : [],
)

async function searchStores() {
  const requestedProduct = product.value.trim()
  const requestedLocation = location.value.trim()

  if (!requestedProduct || !requestedLocation) {
    error.value = 'Enter an item and a location to search.'
    return
  }

  error.value = ''
  stores.value = null
  productGroups.value = null
  searchedProduct.value = requestedProduct
  searchedLocation.value = requestedLocation
  loading.value = true

  try {
    const query = new URLSearchParams({
      zip: requestedLocation,
      product: requestedProduct,
    })
    const response = await fetch(`/search?${query}`)
    let data

    try {
      data = await response.json()
    } catch (parseError) {
      console.error('Unable to parse the store search response:', parseError)
      error.value = 'The search service returned an unreadable response.'
      return
    }

    if (!data || typeof data !== 'object' || Array.isArray(data)) {
      error.value = 'The search service returned an unexpected response.'
      return
    }

    if (!response.ok) {
      error.value = data?.error || `Search failed (${response.status}).`
      return
    }

    if (!Array.isArray(data.nearby_stores)) {
      error.value = 'The search service returned an unexpected response.'
      return
    }

    const responseProducts = data.products
    if (
      !Array.isArray(responseProducts) &&
      (!responseProducts ||
        typeof responseProducts !== 'object' ||
        !productTypes.every(({ key }) => Array.isArray(responseProducts[key])))
    ) {
      error.value = 'The search service returned an unexpected response.'
      return
    }

    stores.value = data.nearby_stores.filter(
      (store) =>
        typeof store?.name === 'string' &&
        typeof store?.address === 'string',
    )
    productGroups.value = Object.fromEntries(
      productTypes.map(({ key }) => {
        const categoryProducts = Array.isArray(responseProducts)
          ? []
          : responseProducts[key]
        return [
          key,
          categoryProducts.filter(
            (item) =>
              typeof item?.name === 'string' &&
              typeof item?.retailer === 'string' &&
              Number.isFinite(item?.price) &&
              typeof item?.size === 'string' &&
              Number.isFinite(item?.unit_price),
          ),
        ]
      }),
    )
  } catch (requestError) {
    console.error('Store search request failed:', requestError)
    error.value =
      'Could not connect to the search service. Make sure the backend is running and try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <a class="brand" href="/" aria-label="ShopScout home">
        <span class="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none">
            <path
              d="M4 5h2l2.2 10.1a2 2 0 0 0 2 1.6h7.4a2 2 0 0 0 1.9-1.4L21 9H7"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
            <circle cx="10.5" cy="20" r="1.2" fill="currentColor" />
            <circle cx="18" cy="20" r="1.2" fill="currentColor" />
          </svg>
        </span>
        <span>ShopScout</span>
      </a>
      <span class="topbar-note">
        <span class="status-dot"></span>
        Your neighborhood, better shopped
      </span>
    </header>

    <main>
      <section class="hero">
        <p class="eyebrow">A LITTLE CLOSER TO YOUR NEXT SHOP</p>
        <h1>Find a store<br />near <span>you.</span></h1>
        <p class="intro">
          Tell us what you need and your ZIP code. We’ll compare prices at
          nearby supported supermarkets.
        </p>

        <form class="search-panel" @submit.prevent="searchStores">
          <label class="form-field">
            <span class="field-label">What are you shopping for?</span>
            <span class="input-wrap">
              <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path
                  d="M5 7h14l-1.2 12H6.2L5 7Z"
                  stroke="currentColor"
                  stroke-width="1.7"
                  stroke-linejoin="round"
                />
                <path
                  d="M9 9V6a3 3 0 0 1 6 0v3"
                  stroke="currentColor"
                  stroke-width="1.7"
                  stroke-linecap="round"
                />
              </svg>
              <input
                v-model="product"
                type="text"
                name="product"
                placeholder="e.g. apples, coffee, pasta"
                autocomplete="off"
                required
              />
            </span>
          </label>

          <span class="panel-divider" aria-hidden="true"></span>

          <label class="form-field location-field">
            <span class="field-label">Where should we look?</span>
            <span class="input-wrap">
              <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path
                  d="M19 10.2c0 5-7 10.3-7 10.3S5 15.2 5 10.2a7 7 0 1 1 14 0Z"
                  stroke="currentColor"
                  stroke-width="1.7"
                  stroke-linejoin="round"
                />
                <circle
                  cx="12"
                  cy="10"
                  r="2.2"
                  stroke="currentColor"
                  stroke-width="1.7"
                />
              </svg>
              <input
                v-model="location"
                type="text"
                name="location"
                placeholder="e.g. 32801"
                autocomplete="postal-code"
                required
              />
            </span>
          </label>

          <button class="search-button" type="submit" :disabled="loading">
            <svg
              v-if="!loading"
              viewBox="0 0 24 24"
              fill="none"
              aria-hidden="true"
            >
              <circle
                cx="10.8"
                cy="10.8"
                r="6.8"
                stroke="currentColor"
                stroke-width="1.8"
              />
              <path
                d="m16 16 4 4"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
              />
            </svg>
            <span>{{ loading ? 'Searching...' : 'Compare prices' }}</span>
          </button>
        </form>

        <p class="search-note">
          Price comparisons are available for supported nearby retailers.
        </p>
      </section>

      <section class="results" aria-live="polite">
        <div v-if="loading" class="message-card">
          <span class="spinner" aria-hidden="true"></span>
          <p>Finding nearby stores and comparing prices...</p>
        </div>

        <div v-else-if="error" class="message-card error-card" role="alert">
          <span class="message-icon" aria-hidden="true">!</span>
          <div>
            <h2>We couldn’t complete that search</h2>
            <p>{{ error }}</p>
          </div>
        </div>

        <template v-else-if="stores !== null">
          <div class="results-heading">
            <div>
              <p class="eyebrow">YOUR SEARCH</p>
              <h2>Results near {{ searchedLocation }}</h2>
              <p class="results-query">For “{{ searchedProduct }}”</p>
            </div>
            <span v-if="products.length" class="result-count">
              {{ products.length }}
              {{ products.length === 1 ? 'comparison' : 'comparisons' }}
            </span>
          </div>

          <section class="product-results" aria-label="Product price comparisons">
            <h2>Price comparisons</h2>
            <div v-if="products.length === 0" class="message-card empty-card">
              <span class="message-icon" aria-hidden="true">?</span>
              <div>
                <h3>No matching products found</h3>
                <p>Try another item or ZIP code.</p>
              </div>
            </div>

            <div
              v-for="type in productTypes"
              v-show="productGroups[type.key].length"
              :key="type.key"
              class="product-group"
            >
              <h3>{{ type.label }} comparison</h3>
              <ul class="product-list">
                <li
                  v-for="(item, index) in productGroups[type.key]"
                  :key="`${item.retailer}-${item.name}-${item.size}-${index}`"
                  class="product-card"
                >
                  <div class="product-details">
                    <h4>{{ item.name }}</h4>
                    <p>{{ item.retailer }} · {{ item.size }}</p>
                  </div>
                  <div class="product-prices">
                    <strong>${{ item.price.toFixed(2) }}</strong>
                    <span>${{ item.unit_price.toFixed(4) }} / {{ type.unit }}</span>
                  </div>
                </li>
              </ul>
            </div>
          </section>

          <section class="nearby-results" aria-label="Nearby supermarkets">
            <h2>Nearby supermarkets</h2>
            <div v-if="stores.length === 0" class="message-card empty-card">
            <span class="message-icon" aria-hidden="true">?</span>
            <div>
              <h2>No nearby supermarkets found</h2>
              <p>Try a nearby city, neighborhood, or ZIP code.</p>
            </div>
          </div>

            <ul v-else class="store-list">
              <li
                v-for="(store, index) in stores"
                :key="`${store.name}-${store.address}`"
                class="store-card"
              >
                <span class="store-number">{{ String(index + 1).padStart(2, '0') }}</span>
                <div class="store-details">
                  <h3>{{ store.name }}</h3>
                  <p>{{ store.address }}</p>
                </div>
                <a
                  class="directions-link"
                  :href="`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(store.address)}`"
                  target="_blank"
                  rel="noopener noreferrer"
                  :aria-label="`Get directions to ${store.name}`"
                >
                  Directions
                  <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
                    <path
                      d="M4 10h11m0 0-4-4m4 4-4 4"
                      stroke="currentColor"
                      stroke-width="1.6"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </a>
              </li>
            </ul>
          </section>
        </template>

        <div v-else class="empty-state">
          <div class="empty-illustration" aria-hidden="true">
            <svg viewBox="0 0 80 80" fill="none">
              <path
                d="M14 30h52l-4 38H18l-4-38Z"
                stroke="currentColor"
                stroke-width="2"
                stroke-linejoin="round"
              />
              <path
                d="M27 33V23a13 13 0 0 1 26 0v10"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
              />
              <path
                d="m32 49 6 6 12-13"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </div>
          <h2>Your next shopping stop starts here</h2>
          <p>Add an item and a location above to see nearby supermarkets.</p>
        </div>
      </section>
    </main>

    <footer class="footer">
      <span>ShopScout</span>
      <span>Find your next stop, close to home.</span>
    </footer>
  </div>
</template>
