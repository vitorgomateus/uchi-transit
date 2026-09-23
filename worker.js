// Cloudflare Worker — drop-in CORS proxy for uchi-transit
// Deploy at: https://dash.cloudflare.com → Workers & Pages → Create Worker
// After deploying, add  "cta_proxy_url": "https://your-worker.workers.dev"
// to your config.json (the part with your CTA API key and stops).

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
};

export default {
  async fetch(request) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS_HEADERS });
    }

    const { searchParams } = new URL(request.url);
    const target = searchParams.get('url');

    if (!target) {
      return new Response('Missing ?url= parameter', { status: 400, headers: CORS_HEADERS });
    }

    // Only allow proxying to the CTA Bus Tracker API and Metra GTFS-RT API
    if (!target.startsWith('https://www.ctabustracker.com/') &&
        !target.startsWith('https://gtfspublic.metrarr.com/')) {
      return new Response('Forbidden', { status: 403, headers: CORS_HEADERS });
    }

    const upstream = await fetch(target);
    return new Response(upstream.body, {
      status: upstream.status,
      headers: {
        ...CORS_HEADERS,
        'Content-Type': upstream.headers.get('Content-Type') ?? 'application/json',
      },
    });
  },
};
