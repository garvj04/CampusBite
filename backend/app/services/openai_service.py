from openai import OpenAI

from app.core.config import OPENAI_API_KEY


def generate_order_insight(order_history: list[dict]) -> str:
    # Use OpenAI when a real API key is configured.
    if (
        OPENAI_API_KEY
        and not OPENAI_API_KEY.lower().startswith("your-")
        and not OPENAI_API_KEY.lower().startswith("your_")
    ):
        client = OpenAI(api_key=OPENAI_API_KEY)

        prompt = (
            "You are a helpful food-ordering assistant for CampusBite. "
            "Analyze the customer's previous orders and provide a short, "
            "useful recommendation based only on the order history.\n\n"
            f"Order history:\n{order_history}\n\n"
            "Give a concise recommendation for what the customer might "
            "like to order next."
        )

        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt
        )

        return response.output_text

    # Fallback when OpenAI is not configured.
    if len(order_history) == 1:
        return (
            "Based on your order history, you may want to try "
            "ordering from the same restaurant again or explore "
            "another item from its menu."
        )

    total_spent = sum(
        order["total_amount"]
        for order in order_history
    )

    average_spend = total_spent / len(order_history)

    return (
        f"You have placed {len(order_history)} orders on CampusBite "
        f"with an average order value of ₹{average_spend:.2f}. "
        "You may want to explore a similar-priced meal from a "
        "restaurant you have ordered from before."
    )
