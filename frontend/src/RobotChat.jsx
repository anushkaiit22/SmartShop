import { useState, useRef, useEffect } from 'react';
import { robotInteract } from './utils/api';

function RobotChat({ onCartIdUpdate }) {
  const [messages, setMessages] = useState([
    { sender: 'robot', text: 'Hi! What product would you like to add to your cart or search for today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [cartId, setCartId] = useState(null);
  const [pendingProductOptions, setPendingProductOptions] = useState(null); // For product selection
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (cartId && onCartIdUpdate) {
      onCartIdUpdate(cartId);
    }
  }, [cartId, onCartIdUpdate]);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const sendMessage = async (userText, lastAction = null, productSelection = null, selectedProductObj = null) => {
    setMessages((msgs) => [...msgs, { sender: 'user', text: userText }]);
    setLoading(true);
    setPendingProductOptions(null);
    try {
      const body = { user_message: userText, cart_id: cartId, last_action: lastAction, platforms: ['flipkart'] };
      if (productSelection !== null) body.product_selection = productSelection;
      if (selectedProductObj) body.selected_product = selectedProductObj;
      
      // Use the API utility function instead of direct fetch
      const data = await robotInteract(userText, cartId, lastAction, ['flipkart'], productSelection, selectedProductObj);
      
      if (!data.success && data.action !== 'select_product') throw new Error(data.message || 'Unknown error');

      if (data.action === 'select_product') {
        setPendingProductOptions(data.data);
        setMessages((msgs) => [...msgs, { sender: 'robot', text: data.message, action: 'select_product', options: data.data }]);
      } else if (data.action === 'confirm_cheapest') {
        setMessages((msgs) => [...msgs, { sender: 'robot', text: data.message, action: 'confirm_cheapest' }]);
      } else if (data.action === 'show_search_results') {
        setMessages((msgs) => [
          ...msgs,
          { sender: 'robot', text: data.message },
          { sender: 'robot', text: renderProducts(data.data) }
        ]);
      } else if (data.action === 'added_to_cart') {
        setCartId(data.cart_id);
        setMessages((msgs) => [
          ...msgs,
          { sender: 'robot', text: data.message },
          { sender: 'robot', text: renderProducts(data.data, true) }
        ]);
      } else {
        setMessages((msgs) => [...msgs, { sender: 'robot', text: data.message }]);
      }
    } catch (err) {
      console.error('Robot interaction error:', err);
      setMessages((msgs) => [...msgs, { sender: 'robot', text: `Sorry, something went wrong: ${err.message}` }]);
    } finally {
      setLoading(false);
      setInput('');
      setTimeout(scrollToBottom, 100);
    }
  };

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    const lastMsg = messages[messages.length - 1];
    if (lastMsg && lastMsg.action === 'confirm_cheapest') {
      if (input.trim().toLowerCase().startsWith('y')) {
        sendMessage('Yes, add the cheapest product', 'confirm_cheapest');
      } else {
        setMessages((msgs) => [...msgs, { sender: 'robot', text: 'Okay, let me know what you want to add or search for!' }]);
        setInput('');
      }
    } else {
      sendMessage(input);
    }
  };

  const handleProductSelect = (idx) => {
    if (!pendingProductOptions || !pendingProductOptions[idx]) return;
    const selectedProduct = pendingProductOptions[idx];
    sendMessage(`Select product ${idx + 1}`, null, idx, selectedProduct);
    setPendingProductOptions(null);
  };

  function renderProducts(products, isCart = false) {
    if (!products || products.length === 0) return isCart ? 'No products added.' : 'No products found.';
    return (
      <div className="robot-products-list">
        {products.map((p, i) => (
          <div key={i} className="robot-product-item">
            {p.images && p.images.length > 0 && p.images[0].url && (
              <img 
                src={p.images[0].url} 
                alt={p.images[0].alt_text || p.name || 'Product image'} 
                style={{ width: 64, height: 64, objectFit: 'contain', marginRight: 8, verticalAlign: 'middle', borderRadius: 4, border: '1px solid #eee' }}
              />
            )}
            <strong>{p.name || p.product_name || 'Product'}</strong> - ₹{p.price?.current_price || p.price || '-'}
            {p.rating && p.rating.rating && (
              <> | {p.rating.rating}★</>
            )}
            {p.delivery && p.delivery.delivery_time && (
              <> | {p.delivery.delivery_time}</>
            )}
            {p.platform && (
              <> | <span className="robot-platform">{p.platform.toUpperCase()}</span></>
            )}
            {p.platform_url && (
              <> | <a href={p.platform_url} target="_blank" rel="noopener noreferrer">View</a></>
            )}
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="robot-chat-container">
      <div className="robot-chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`robot-message ${msg.sender}`}>{typeof msg.text === 'string' ? msg.text : msg.text}</div>
        ))}
        {pendingProductOptions && (
          <div className="robot-message robot">
            <div>Please select a product to add:</div>
            <div className="robot-products-list">
              {pendingProductOptions.map((p, i) => (
                <div key={i} className="robot-product-item" style={{ cursor: 'pointer', border: '1px solid #1976d2', marginBottom: 8 }} onClick={() => handleProductSelect(i)}>
                  <strong>{p.name || p.product_name || 'Product'}</strong> - ₹{p.price?.current_price || p.price || '-'}
                  {p.rating && p.rating.rating && (
                    <> | {p.rating.rating}★</>
                  )}
                  {p.delivery && p.delivery.delivery_time && (
                    <> | {p.delivery.delivery_time}</>
                  )}
                  {p.platform && (
                    <> | <span className="robot-platform">{p.platform.toUpperCase()}</span></>
                  )}
                  {p.platform_url && (
                    <> | <a href={p.platform_url} target="_blank" rel="noopener noreferrer">View</a></>
                  )}
                  <div style={{ color: '#1976d2', fontWeight: 'bold', marginTop: 4 }}>Add this</div>
                </div>
              ))}
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form className="robot-chat-input" onSubmit={handleSend}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={loading ? 'Robot is thinking...' : 'Type your message...'}
          disabled={loading || !!pendingProductOptions}
        />
        <button type="submit" disabled={loading || !input.trim() || !!pendingProductOptions}>{loading ? '...' : 'Send'}</button>
      </form>
    </div>
  );
}

export default RobotChat; 