Possible refernce for CLI Validator:
              HTTPie Cli
        HTTPie is a modern, open-source command-line HTTP client used to send HTTP requests (GET, POST, PUT, DELETE, etc.) directly from the terminal.
        RELEVANCE:
               1. demonstration of real,Production-based CLI.
               2. thin and resuable CLI.
               3. separate commamd handling from business logic.
        (HTTPie CLI is reference architecture)
        ARCHITECTURE:
                CLI Layer (Parses command-line arguments ,Handles flags (--json, --headers, etc.))
                    ↓
           Adapters / Output Layer (Formats responses (pretty print, JSON, raw))
                    ↓
                Core Logic    (Build HTTP request model and validates input)
                     ↓
              Execution Engine (send actual http request , network I/O)
        WHAT NOT TO TAKE FROM HTTPie CLI
               1.HTTPie is exploratory and user-friendly.Our tool is authoritative and strict.
               2.HTTPie’s HTTP logic is irrelevant to us.We only copy structure, not implementation

AIM: Build CLI but follow HTTPie's separation between CLI AND core.Even if CLI changes the core should remain untouched.
