from aws_cdk import App
from stack.url_shortener_stack import UrlShortenerStack

app = App()
UrlShortenerStack(app, "urlshort-app")

app.synth()
