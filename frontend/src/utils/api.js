// API utility functions for SmartShop frontend

// Get the base API URL from environment or use relative path
const getApiBaseUrl = () => {
  // Use relative path for both development and production
  // This will work with the Vercel proxy configuration
  return '';
};

// Create full API URL
export const createApiUrl = (endpoint) => {
  const baseUrl = getApiBaseUrl();
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${baseUrl}${cleanEndpoint}`;
};

// API request helper
export const apiRequest = async (endpoint, options = {}) => {
  const url = createApiUrl(endpoint);
  
  console.log('Making API request to:', url); // Debug log
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  const response = await fetch(url, { ...defaultOptions, ...options });
  
  console.log('API response status:', response.status); // Debug log
  
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
};

// Specific API functions
export const searchProducts = async (query, platforms = [], limit = 20) => {
  const params = new URLSearchParams({
    q: query,
    limit: limit.toString(),
  });
  
  if (platforms.length > 0) {
    params.append('platforms', platforms.join(','));
  }
  
  return apiRequest(`/api/v1/search/?${params.toString()}`);
};

export const getCart = async (cartId) => {
  return apiRequest(`/api/v1/cart/${cartId}`);
};

export const addToCart = async (cartId, product, quantity = 1, platform = null) => {
  return apiRequest(`/api/v1/cart/${cartId}/add`, {
    method: 'POST',
    body: JSON.stringify({
      product: product,
      quantity: quantity,
      selected_platform: platform || product.platform,
    }),
  });
};

export const robotInteract = async (userMessage, cartId = null, lastAction = null, platforms = ['flipkart'], productSelection = null, selectedProduct = null) => {
  const body = {
    user_message: userMessage,
    cart_id: cartId,
    last_action: lastAction,
    platforms: platforms,
  };
  
  if (productSelection !== null) {
    body.product_selection = productSelection;
  }
  
  if (selectedProduct !== null) {
    body.selected_product = selectedProduct;
  }
  
  return apiRequest('/api/v1/robot/interact', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}; 