from app.sources.public_feed import DemoPublicFeedSource
from app.sources.remotive import RemotiveSource

SOURCE_REGISTRY = {"demo_public_feed": DemoPublicFeedSource, "remotive": RemotiveSource}
