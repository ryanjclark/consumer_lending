from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

lang_client = language.LanguageServiceClient()


def analyze(text):
    """ Returns sentiment analysis score """
    doc = types.Document(content=text, type=enums.Document.Type.PLAIN_TEXT)
    sentiment = lang_client.analyze_sentiment(document=doc).document_sentiment
    return sentiment.score
