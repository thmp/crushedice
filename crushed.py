from twisted.internet import reactor
from crusher.worker import *
from crusher import datasource
import config

crushedIceDataSource = datasource.MongoDataSource(config.MONGO_URL, config.MONGO_DB)
crushedIceWorker = Worker(crushedIceDataSource)

reactor.callWhenRunning(crushedIceWorker.parse_rss)
reactor.run()