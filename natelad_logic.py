def generate_response(message):
    msg = message.lower()
    if "price" in msg:
        return "Our pricing details are available at https://nateladagency.com/pricing"
    elif "call" in msg or "contact" in msg:
        return "You can call us directly at +263XXXXXXXX."
    elif "services" in msg or "offer" in msg:
        return "We offer branding, web design, automation, and more. How can we help your business today?"
    elif "website" in msg:
        return "Visit https://nateladagency.com for more information."
    else:
        return "Hello! Welcome to Natelad Agency. What service are you interested in?"
