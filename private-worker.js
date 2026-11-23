// Mnemora Private MCP
// Secure bootstrap: deny all requests until
// authentication and private backend are configured.

export default {
  async fetch(request, env) {
    return new Response(
      JSON.stringify({
        error: "private_mcp_not_configured"
      }),
      {
        status: 403,
        headers: {
          "content-type": "application/json",
          "cache-control": "no-store"
        }
      }
    );
  }
};
