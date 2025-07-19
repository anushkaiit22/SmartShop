from fastapi import APIRouter, HTTPException, Body
from typing import Optional
import logging

from app.services.nlp.query_parser import query_parser
from app.services.search_service import search_service
from app.services.cart.cart_service import cart_service
from app.models.product import ProductSearchRequest, Product
from app.models.cart import CartResponse

logger = logging.getLogger(__name__)

router = APIRouter()



# Add explicit OPTIONS handler for CORS preflight
@router.options("/interact")
async def robot_interact_options():
    return {"message": "OK"}

@router.post("/interact")
async def robot_interact(
    user_message: str = Body(..., description="User's message to the robot"),
    cart_id: Optional[str] = Body(None, description="Cart ID (optional, for stateless mode)"),
    last_action: Optional[str] = Body(None, description="Last robot action (for context)"),
    platforms: Optional[list] = Body(None, description="List of platforms to restrict search to (e.g., ['flipkart'])"),
    product_selection: Optional[int] = Body(None, description="Index of product selected by user for confirmation (0-based)"),
    selected_product: Optional[dict] = Body(None, description="Full product object selected by user (for stateless selection)")
):
    """
    Interactive robot endpoint: interprets user message, asks for confirmation if vague, shows top products for confirmation, adds to cart or shows search results.
    """
    try:
        # If selected_product is provided, add it directly to cart
        if selected_product is not None:
            # Reconstruct Product object from dict
            product_obj = Product(**selected_product)
            quantity = selected_product.get('quantity', 1)
            if not cart_id:
                cart = await cart_service.create_cart()
                cart_id = cart.id
            else:
                cart = await cart_service.get_cart(cart_id)
                if not cart:
                    cart = await cart_service.create_cart()
                    cart_id = cart.id
            await cart_service.add_item_to_cart(cart_id, product_obj, quantity=quantity)
            return {
                "success": True,
                "action": "added_to_cart",
                "message": f"Added '{getattr(product_obj, 'name', 'the product')}' to your cart.",
                "cart_id": cart_id,
                "data": [product_obj]
            }

        parsed_query = await query_parser.parse_query(user_message)
        products = parsed_query.products
        constraints = parsed_query.constraints

        if not products and last_action == "confirm_cheapest":
            # Only try to create a product if we have a fallback type
            if hasattr(parsed_query, 'products') and isinstance(parsed_query.products, list) and len(parsed_query.products) > 0:
                products = [type(parsed_query.products[0])(
                    product_name=user_message.strip(),
                    quantity=1
                )] if user_message.strip() else []
            else:
                products = []

        if not products:
            return {
                "success": True,
                "action": "confirm_cheapest",
                "message": "You didn't specify a product. Should I add the cheapest available product to your cart?",
                "data": None
            }

        search_platforms = platforms if platforms else None

        if any(word in user_message.lower() for word in ["check", "show", "search", "find", "look for"]):
            search_term = products[0].product_name if products and hasattr(products[0], 'product_name') else user_message
            search_request = ProductSearchRequest(query=search_term, limit=5, platforms=search_platforms)
            response = await search_service.search_products(search_request)
            return {
                "success": True,
                "action": "show_search_results",
                "message": f"Here are the results for '{search_term}':",
                "data": response.data.products if response.success else []
            }

        # Step: Show top 3-5 matching products for confirmation before adding
        # Only proceed to add if product_selection is provided
        if not products or len(products) == 0:
            return {
                "success": False,
                "action": "no_results",
                "message": "Sorry, I couldn't understand which product you want to add. Please try rephrasing your request.",
                "data": []
            }
        main_intent = products[0]
        search_request = ProductSearchRequest(query=main_intent.product_name, limit=5, platforms=search_platforms, max_price=getattr(main_intent, 'max_price', None), min_rating=getattr(main_intent, 'min_rating', None))
        response = await search_service.search_products(search_request)
        if not response.success or not response.data.products:
            return {
                "success": False,
                "action": "no_results",
                "message": f"No products found for '{getattr(main_intent, 'product_name', 'your query')}'.",
                "data": []
            }
        filtered_products = [p for p in response.data.products if getattr(main_intent, 'product_name', '').lower() in (getattr(p, 'name', '') or '').lower()]
        if not filtered_products:
            filtered_products = response.data.products
        top_products = filtered_products[:5]

        if not top_products or len(top_products) == 0:
            return {
                "success": False,
                "action": "no_results",
                "message": "No matching products found to add to your cart.",
                "data": []
            }

        if product_selection is None:
            # Ask user to select which product to add
            return {
                "success": True,
                "action": "select_product",
                "message": f"Please select which product to add to your cart:",
                "data": top_products
            }
        # Add the selected product to cart
        selected_idx = product_selection
        if selected_idx < 0 or selected_idx >= len(top_products):
            return {
                "success": False,
                "action": "invalid_selection",
                "message": "Invalid product selection.",
                "data": top_products
            }
        selected_product = top_products[selected_idx]
        if not cart_id:
            cart = await cart_service.create_cart()
            cart_id = cart.id
        else:
            cart = await cart_service.get_cart(cart_id)
            if not cart:
                cart = await cart_service.create_cart()
                cart_id = cart.id
        await cart_service.add_item_to_cart(cart_id, selected_product, quantity=getattr(main_intent, 'quantity', 1))
        return {
            "success": True,
            "action": "added_to_cart",
            "message": f"Added '{getattr(selected_product, 'name', 'the product')}' to your cart.",
            "cart_id": cart_id,
            "data": [selected_product]
        }
    except Exception as e:
        logger.error(f"Robot interaction error: {e}")
        return {
            "success": False,
            "action": "error",
            "message": f"An error occurred: {str(e)}",
            "data": []
        } 