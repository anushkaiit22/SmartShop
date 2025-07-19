import { useState } from 'react';
import './App.css';
import RobotChat from './RobotChat';

const TABS = [
  { label: 'Robot Assistant', value: 'robot' },
  { label: 'Quick Commerce', value: 'quick' },
  { label: 'E-Commerce', value: 'ecom' },
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
        platformFilter = 'flipkart,amazon,meesho';
      } else if (activeTab === 'quick') {
        platformFilter = 'blinkit';
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
        const platformOrder = ['flipkart', 'amazon', 'meesho'];
        products.sort((a, b) => {
          const aIndex = platformOrder.indexOf(a.platform);
          const bIndex = platformOrder.indexOf(b.platform);
          return aIndex - bIndex;
        });
      } else if (activeTab === 'quick') {
        const platformOrder = ['blinkit'];
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
    <div className="main-container" style={{ 
      display: 'flex', 
      height: '100vh', 
      width: '100vw',
      position: 'fixed',
      top: 0,
      left: 0,
      overflow: 'hidden',
      margin: 0,
      padding: '0 40px',
      boxSizing: 'border-box'
    }}>
      {/* View Cart button at top right */}
      <button className="view-cart-btn top-right" onClick={openCartModal} title="View Cart" style={{ position: 'absolute', top: 24, right: 40, zIndex: 10 }}>
        🛒 View Cart
      </button>
      {/* Robot image at bottom right */}
      <div className="robot-image-container" style={{ position: 'absolute', bottom: 20, right: 20, zIndex: 5, width: 120, height: 120 }}>
        <img 
          src="/robot-shopping-cart.png" 
          alt="Shopping Robot Assistant" 
          style={{ width: '100%', height: '100%', objectFit: 'contain' }}
        />
      </div>
      {/* Sidebar for vertical tabs */}
      <div className="sidebar-tabs" style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'flex-start', 
        gap: 16, 
        marginRight: 32, 
        minWidth: 180, 
        height: '100vh', 
        justifyContent: 'flex-end', 
        position: 'relative', 
        paddingTop: 32, 
        paddingBottom: 32,
        overflow: 'hidden'
      }}>
        {/* App title at the top of the sidebar */}
        <h1 className="app-title sidebar-title" style={{ color: 'white', fontSize: 28, margin: 0, marginBottom: 32, textAlign: 'left', letterSpacing: 2, fontWeight: 700, textShadow: '0 2px 4px rgba(0,0,0,0.3)', position: 'sticky', top: 0, zIndex: 20, backgroundColor: '#232946', padding: '8px 0' }}>Smart Shop</h1>
        <div style={{ flex: 1, minHeight: 40 }} />
        <div style={{ display: 'flex', flexDirection: 'column', width: '100%', gap: 8, marginBottom: 48 }}>
        {TABS.map((tab) => (
          <button
            key={tab.value}
              className={`tab-btn-vertical${activeTab === tab.value ? ' active' : ''}`}
            onClick={() => setActiveTab(tab.value)}
              style={{ width: '100%', textAlign: 'left', padding: '14px 24px', fontSize: 17, marginBottom: 8 }}
          >
            {tab.label}
          </button>
        ))}
        </div>
      </div>
      {/* Main content area */}
      <div className="main-content-centered" style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        overflow: 'hidden',
        padding: '20px 0'
      }}>
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
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '100%', height: '100%' }}>
        <RobotChat onCartIdUpdate={handleCartIdUpdate} />
          </div>
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
          <div className="results-section" style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            maxHeight: 'calc(100vh - 200px)'
          }}>
            {results.length > 0 ? (
              <div className="platform-results" style={{
                flex: 1,
                overflow: 'hidden',
                display: 'flex',
                flexDirection: 'column'
              }}>
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
                    <div key={platform} className="platform-table" style={{
                      flex: 1,
                      display: 'flex',
                      flexDirection: 'column',
                      overflow: 'hidden',
                      maxHeight: '100%'
                    }}>
                      <h3 className="platform-title">{platform.toUpperCase()}</h3>
                      <div className="results-table" style={{
                        flex: 1,
                        overflow: 'auto',
                        maxHeight: 'calc(100% - 60px)'
                      }}>
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
    </div>
  );
}

export default App;
