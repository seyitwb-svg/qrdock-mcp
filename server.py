#!/usr/bin/env python3
"""qrdock-mcp — MCP stdio server: QR code generation tools.
Zero external services: QR codes are generated locally with segno.
"""
import base64, io, json, sys

try:
    import segno
except ImportError:
    sys.stderr.write("segno required: pip install segno\n")
    sys.exit(1)

TOOLS = [
    {
        "name": "qr_png",
        "description": "Generate a QR code as a PNG image (base64). Returns the image ready to save or embed.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text or URL to encode"},
                "scale": {"type": "integer", "default": 8, "description": "Pixels per QR module (1-20)"},
                "dark": {"type": "string", "description": "Foreground color, e.g. '#1a1a2e' or 'black'"},
                "light": {"type": "string", "description": "Background color"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "qr_svg",
        "description": "Generate a QR code as SVG markup — infinitely scalable, embeds directly in HTML/markdown.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text or URL to encode"},
                "scale": {"type": "integer", "default": 4, "description": "SVG scale factor"},
                "dark": {"type": "string", "description": "Foreground color"},
                "light": {"type": "string", "description": "Background color"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "qr_ascii",
        "description": "Generate a QR code as ASCII/terminal art (UTF-8 block characters). Scannable in a terminal.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text or URL to encode"},
            },
            "required": ["text"],
        },
    },
]

def make_qr(text):
    return segno.make(text, error="m")

def call(name, args):
    if name == "qr_ascii":
        q = make_qr(args["text"])
        buf = io.StringIO()
        q.save(buf, kind="txt", border=2)
        art = buf.getvalue().translate(str.maketrans({"0": "  ", "1": "\u2588\u2588"}))
        return [{"type": "text", "text": art}]
    q = make_qr(args["text"])
    buf = io.BytesIO()
    kw = {}
    if args.get("dark"): kw["dark"] = args["dark"]
    if args.get("light"): kw["light"] = args["light"]
    if name == "qr_png":
        q.save(buf, kind="png", scale=int(args.get("scale", 8)), border=2, **kw)
        return [
            {"type": "text", "text": f"QR PNG for {args['text']!r} — {len(buf.getvalue())} bytes"},
            {"type": "image", "data": base64.b64encode(buf.getvalue()).decode(), "mimeType": "image/png"},
        ]
    if name == "qr_svg":
        q.save(buf, kind="svg", scale=int(args.get("scale", 4)), border=2, xmldecl=False, **kw)
        return [{"type": "text", "text": buf.getvalue().decode()}]
    return [{"type": "text", "text": f"unknown tool {name}", "isError": True}]

def reply(rid, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": rid}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        rid, method, params = req.get("id"), req.get("method"), req.get("params", {})
        if rid is None:
            continue  # notification
        if method == "initialize":
            reply(rid, {
                "protocolVersion": params.get("protocolVersion", "2024-11-05"),
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "qrdock-mcp", "version": "1.0.0"},
            })
        elif method == "tools/list":
            reply(rid, {"tools": TOOLS})
        elif method == "tools/call":
            try:
                content = call(params.get("name"), params.get("arguments", {}))
                reply(rid, {"content": content})
            except Exception as e:
                reply(rid, {"content": [{"type": "text", "text": f"error: {e}"}], "isError": True})
        elif method == "ping":
            reply(rid, {})
        else:
            reply(rid, error={"code": -32601, "message": f"method not found: {method}"})

if __name__ == "__main__":
    main()
