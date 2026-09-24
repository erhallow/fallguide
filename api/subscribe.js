// Vercel keeps beehiiv_api on the server; it is never included in page assets.
module.exports = require('../lib/subscribe.cjs').createSubscribeHandler();
