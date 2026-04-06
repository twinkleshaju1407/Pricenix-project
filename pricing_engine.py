from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def evaluate_price(our_price, competitor_price):
    """
    Rule-based pricing engine:

    - If competitor price < our price
    - Allow max 3% discount
    - Final price cannot go below competitor price
    """

    if competitor_price >= our_price:
        return our_price, 0

    price_gap = our_price - competitor_price
    max_discount = our_price * 0.03  # 3%

    # Apply discount rule
    applied_discount = min(price_gap, max_discount)
    new_price = our_price - applied_discount

    # Ensure we don't undercut competitor unnecessarily
    final_price = max(new_price, competitor_price)

    return round(final_price, 2), round(price_gap, 2)


def analyze_sentiment(text):
    """
    Analyzes text sentiment and returns a score and label.
    """
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)
    score = sentiment['compound']

    if score >= 0.05:
        label = "Positive"
    elif score <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    return round(score, 2), label
