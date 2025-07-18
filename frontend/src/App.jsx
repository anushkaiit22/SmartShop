import { useState } from 'react';
import './App.css';
import RobotChat from './RobotChat';

const TABS = [
  { label: 'Quick Commerce', value: 'quick' },
  { label: 'E-Commerce', value: 'ecom' },
  { label: 'Robot Assistant', value: 'robot' },
];

function App() {
  const [activeTab, setActiveTab] = useState('quick');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [cartModalOpen, setCartModalOpen] = useState(false);
  const [cartId, setCartId] = useState(null);
  const [cartData, setCartData] = useState(null);
  const [cartLoading, setCartLoading] = useState(false);
  const [cartError, setCartError] = useState(null);

  // Listen for cartId updates from RobotChat
  const handleCartIdUpdate = (id) => {
    setCartId(id);
  };

  const openCartModal = async () => {
    if (!cartId) {
      setCartError('No cart ID available. Add something to your cart first!');
      setCartData(null);
      setCartModalOpen(true);
      return;
    }
    setCartLoading(true);
    setCartError(null);
    setCartModalOpen(true);
    try {
      const res = await fetch(`/api/v1/cart/${cartId}`);
      const data = await res.json();
      if (!data.success) throw new Error(data.error || 'Failed to fetch cart');
      setCartData(data.data);
    } catch (err) {
      setCartError(err.message);
      setCartData(null);
    } finally {
      setCartLoading(false);
    }
  };

  const closeCartModal = () => {
    setCartModalOpen(false);
    setCartError(null);
  };

  const handleManualCartId = (e) => {
    setCartId(e.target.value);
  };

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
        platformFilter = 'flipkart,amazon,meesho,nykaa';
      } else if (activeTab === 'quick') {
        platformFilter = 'blinkit,zepto,instamart';
      }
      const res = await fetch(
        `/api/v1/search/?q=${encodeURIComponent(query)}&limit=20&platforms=${platformFilter}`,
        { method: 'GET' }
      );
      if (!res.ok) throw new Error('Failed to fetch results');
      const data = await res.json();
      if (!data.success) throw new Error(data.error || 'Unknown error');
      let products = [];
      if (data.data && data.data.products) {
        products = data.data.products;
      } else if (data.products) {
        products = data.products;
      } else if (Array.isArray(data)) {
        products = data;
      }
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
      setResults(products);
    } catch (err) {
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
        <button className="view-cart-btn" onClick={openCartModal} title="View Cart">
          🛒 View Cart
        </button>
      </div>
      {cartModalOpen && (
        <div className="cart-modal-overlay" onClick={closeCartModal}>
          <div className="cart-modal" onClick={e => e.stopPropagation()}>
            <button className="close-cart-modal" onClick={closeCartModal}>×</button>
            <h2>Your Cart</h2>
            <div style={{ marginBottom: 8 }}>
              <label>Cart ID: </label>
              <input value={cartId || ''} onChange={handleManualCartId} placeholder="Enter cart ID" style={{ width: 200 }} />
              <button onClick={openCartModal} style={{ marginLeft: 8 }}>Load</button>
            </div>
            {cartLoading ? (
              <div>Loading...</div>
            ) : cartError ? (
              <div className="error-msg">{cartError}</div>
            ) : cartData ? (
              <div>
                <div><strong>Total Items:</strong> {cartData.total_items}</div>
                <div><strong>Total Price:</strong> ₹{cartData.total_price}</div>
                <div style={{ marginTop: 12 }}>
                  {cartData.items && cartData.items.length > 0 ? (
                    <ul>
                      {cartData.items.map((item, idx) => (
                        <li key={idx}>
                          <strong>{item.product.name}</strong> x{item.quantity} - ₹{item.product.price.current_price} ({item.selected_platform})
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <div>No items in cart.</div>
                  )}
                </div>
              </div>
            ) : (
              <div>No cart loaded.</div>
            )}
          </div>
        </div>
      )}
      {activeTab === 'robot' ? (
        <RobotChat onCartIdUpdate={handleCartIdUpdate} />
      ) : (
        <>
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
            {results.length > 0 ? (
              <div className="platform-results">
                {(() => {
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
        </>
      )}
    </div>
  );
}

export default App;
