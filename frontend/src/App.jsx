import { useState } from 'react';
import './App.css';

const TABS = [
  { label: 'Quick Commerce', value: 'quick' },
  { label: 'E-Commerce', value: 'ecom' },
];

function App() {
  const [activeTab, setActiveTab] = useState('quick');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setResults([]);
    try {
      // Define platform filters based on tab
      let platformFilter = '';
      if (activeTab === 'ecom') {
        // E-commerce: Flipkart first, then others (exclude quick commerce)
        platformFilter = 'flipkart,amazon,meesho,nykaa';
      } else if (activeTab === 'quick') {
        // Quick Commerce: only Blinkit, Zepto, Instamart
        platformFilter = 'blinkit,zepto,instamart';
      }
      
      // Use the correct backend API endpoint with platform filter
      const res = await fetch(
        `/api/v1/search/?q=${encodeURIComponent(query)}&limit=20&platforms=${platformFilter}`,
        { method: 'GET' }
      );
      if (!res.ok) throw new Error('Failed to fetch results');
      const data = await res.json();
      console.log('API Response:', data); // Debug log
      
      if (!data.success) throw new Error(data.error || 'Unknown error');
      
      // Handle different response structures
      let products = [];
      if (data.data && data.data.products) {
        products = data.data.products;
      } else if (data.products) {
        products = data.products;
      } else if (Array.isArray(data)) {
        products = data;
      }
      
      // Sort products by platform order to match the requested order
      if (activeTab === 'ecom') {
        const platformOrder = ['flipkart', 'amazon', 'meesho', 'nykaa'];
        products.sort((a, b) => {
          const aIndex = platformOrder.indexOf(a.platform);
          const bIndex = platformOrder.indexOf(b.platform);
          return aIndex - bIndex;
        });
      } else if (activeTab === 'quick') {
        const platformOrder = ['blinkit', 'zepto', 'instamart'];
        products.sort((a, b) => {
          const aIndex = platformOrder.indexOf(a.platform);
          const bIndex = platformOrder.indexOf(b.platform);
          return aIndex - bIndex;
        });
      }
      
      console.log('Parsed products:', products); // Debug log
      setResults(products);
    } catch (err) {
      console.error('Search error:', err); // Debug log
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="main-container">
      <h1 className="app-title">Product Comparator</h1>
      <div className="tabs">
        {TABS.map((tab) => (
          <button
            key={tab.value}
            className={`tab-btn${activeTab === tab.value ? ' active' : ''}`}
            onClick={() => setActiveTab(tab.value)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <form className="search-bar" onSubmit={handleSearch}>
        <input
          type="text"
          placeholder={`Search products in ${TABS.find(t => t.value === activeTab).label}...`}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>
      {error && <div className="error-msg">{error}</div>}
      <div className="results-section">
        {console.log('Rendering results:', results)} {/* Debug log */}
        {results.length > 0 ? (
          <div className="platform-results">
            {(() => {
              // Group products by platform
              const groupedProducts = results.reduce((acc, product) => {
                const platform = product.platform || 'Unknown';
                if (!acc[platform]) {
                  acc[platform] = [];
                }
                acc[platform].push(product);
                return acc;
              }, {});
              
              return Object.entries(groupedProducts).map(([platform, products]) => (
                <div key={platform} className="platform-table">
                  <h3 className="platform-title">{platform.toUpperCase()}</h3>
                  <div className="results-table">
                    <div className="results-header">
                      <span>Product</span>
                      <span>Price</span>
                      <span>Rating</span>
                      <span>Delivery</span>
                      <span>Link</span>
                    </div>
                    {products.map((item, idx) => (
                      <div className="results-row" key={idx}>
                        <span className="product-name">{item.name || 'No name'}</span>
                        <span className="product-price">
                          {item.price && item.price.current_price ? (
                            (() => {
                              let price = item.price.current_price;
                              if (item.platform === 'flipkart') {
                                // Only fix if price is 6 digits or more (>= 100000)
                                if (
                                  price >= 100000 &&
                                  price % 10 === 0 &&
                                  Math.round(price / 10) >= 1000 && Math.round(price / 10) <= 200000
                                ) {
                                  price = Math.round(price / 10);
                                }
                              }
                              return `₹${price.toLocaleString('en-IN')}`;
                            })()
                          ) : '-'}
                          {item.price && item.price.original_price && item.price.original_price > item.price.current_price && (
                            <span className="original-price">
                              {(() => {
                                let originalPrice = item.price.original_price;
                                if (item.platform === 'flipkart') {
                                  if (
                                    originalPrice >= 100000 &&
                                    originalPrice % 10 === 0 &&
                                    Math.round(originalPrice / 10) >= 1000 && Math.round(originalPrice / 10) <= 200000
                                  ) {
                                    originalPrice = Math.round(originalPrice / 10);
                                  }
                                }
                                return `₹${originalPrice.toLocaleString('en-IN')}`;
                              })()}
                            </span>
                          )}
                        </span>
                        <span className="product-rating">
                          {item.rating && item.rating.rating ? `${item.rating.rating}★ (${item.rating.total_reviews})` : '-'}
                        </span>
                        <span className="product-delivery">
                          {item.delivery && item.delivery.delivery_time ? item.delivery.delivery_time : '-'}
                        </span>
                        <a href={item.platform_url || '#'} target="_blank" rel="noopener noreferrer" className="product-link">View</a>
                      </div>
                    ))}
                  </div>
                </div>
              ));
            })()}
          </div>
        ) : (
          <div className="no-results">
            {loading ? 'Searching...' : `No results to display. (Results count: ${results.length})`}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
