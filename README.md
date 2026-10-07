# qrdock-mcp — QR codes for your agent

An [MCP](https://modelcontextprotocol.io) stdio server that gives AI agents QR code generation — locally, no API keys, no network calls, no accounts.

Three tools:

| tool | output |
|------|--------|
| `qr_png` | base64 PNG (scale + custom colors) |
| `qr_svg` | SVG markup for embedding |
| `qr_ascii` | terminal-scannable block-art QR |

~120 lines of Python + `segno`. MIT.

## Install

```bash
pip install segno
```

## Configure

```json
{
  "mcpServers": {
    "qrdock": {
      "command": "python3",
      "args": ["/path/to/qrdock-mcp/server.py"]
    }
  }
}
```

## Example

Ask your agent: "make me a QR code for https://seyitwb-svg.github.io/qrdock/" — it returns a PNG you can save or render inline.

## Related

- [QRDock](https://github.com/seyitwb-svg/qrdock) — the full self-hosted QR service this is inspired by (retargetable codes, scan analytics, one Docker container). MIT.
- [Grand Line fleet](https://github.com/seyitwb-svg/grand-line-fleet) — 20 more self-hosted micro-SaaS tools.

License: MIT
