# TradingYourModel — Design Document

**VS Code Note:** This file uses Mermaid diagrams. Install the **Markdown Preview Mermaid Support** extension (bierner.markdown-mermaid) in VS Code to render them. Alternatively, open this file in GitHub or any Mermaid-compatible viewer.

## "Ask LLM" Button Flowchart

The diagram below illustrates the end-to-end data flow when the user clicks the **Ask LLM** button in the Model tab.

```mermaid
flowchart TD
    A["User clicks 'Ask LLM'"]
    A --> B["Frontend (LeftPanel.tsx)<br/>handleAskLLM()"]

    B --> C["window.api.modelBull()"]
    B --> D["window.api.modelBear()"]

    C --> E["preload.js → ipcRenderer.invoke('model_bull')"]
    D --> F["preload.js → ipcRenderer.invoke('model_bear')"]

    E --> G["main.js → ipcMain.handle('model_bull')<br/>spawn python python_bridge.py"]
    F --> H["main.js → ipcMain.handle('model_bear')<br/>spawn python python_bridge.py"]

    G --> I["python_bridge.py handle_model_request()"]
    H --> J["python_bridge.py handle_model_request()"]

    I --> K["yfinance fetch close price + indicator data"]
    I --> L["If includeFundamental → yfinance fundamentals"]
    J --> M["yfinance fetch close price + indicator data"]
    J --> N["If includeFundamental → yfinance fundamentals"]

    K --> O["get_bull_comment(symbol, indicators, close_price, extra_info, fundamental_info)"]
    L --> O
    M --> P["get_bear_comment(symbol, indicators, close_price, extra_info, fundamental_info)"]
    N --> P

    O --> Q["OpenRouter API (bullish prompt)"]
    P --> R["OpenRouter API (bearish prompt)"]

    Q --> S["Returns JSON → {comment, close_price, indicator_data, fundamental_info}"]
    R --> T["Returns JSON → {comment, close_price, indicator_data, fundamental_info}"]

    S --> U["Frontend parses JSON → extracts bullComment + closePrice + indicatorData + fundamentalInfo"]
    T --> V["Frontend parses JSON → extracts bearComment + closePrice + indicatorData + fundamentalInfo"]

    U --> W["window.api.modelRecommend(symbol, indicators, closePrice, indicatorData, fundamentalInfo, bullComment, bearComment)"]
    V --> W

    W --> X["main.js → ipcMain.handle('model_recommend') → spawn python python_bridge.py"]
    X --> Y["python_bridge.py handle_model_recommend()"]
    Y --> Z["openrouter_client.py get_recommendation()"]

    Z --> AA["OpenRouter API (neutral fact-check prompt)"]
    AA --> AB["Returns fact-check + BUY / SELL / HOLD"]

    AB --> AC["RightPanel displays Bull → Bear → Recommendation"]
```

## Sequence Summary

1. **User clicks "Ask LLM"** — triggers `handleAskLLM()` in `LeftPanel.tsx`.
2. **Parallel bull/bear calls** — `modelBull()` and `modelBear()` are invoked simultaneously via the Electron IPC bridge.
3. **Python bridge data gathering** — each call fetches the latest close price, technical indicator data from `yfinance`, and optionally fundamental data.
4. **LLM analysis** — `get_bull_comment()` and `get_bear_comment()` send requests to the OpenRouter API with bullish/bearish system prompts.
5. **JSON-encoded response** — the Python bridge now returns `{comment, close_price, indicator_data, fundamental_info}` so the frontend has all auxiliary data without re-fetching.
6. **Recommendation step** — the frontend calls `modelRecommend()` with the symbol, indicators, close price, indicator data, fundamentals, and both bull/bear comments.
7. **Fact-check and final verdict** — `get_recommendation()` sends a neutral prompt to OpenRouter asking it to fact-check the bull/bear claims against the actual data and produce a **BUY / SELL / HOLD** recommendation.
8. **Display** — the right panel shows the bull comment, bear comment, and recommendation (with fact-check details) in order.

## Architecture Layers

| Layer          | Technology              | Files                                               |
| -------------- | ----------------------- | --------------------------------------------------- |
| UI (React)     | TypeScript, MUI         | `LeftPanel.tsx`, `RightPanel.tsx`, `App.tsx`        |
| IPC Bridge     | Electron preload        | `preload.js`                                        |
| Main Process   | Electron (Node.js)      | `main.js`                                           |
| Python Backend | Python 3                | `python_bridge.py`                                  |
| Data Fetching  | yfinance                | `tradingyourmodel/dataflows/y_finance.py`           |
| LLM Client     | urllib → OpenRouter API | `tradingyourmodel/llm/clients/openrouter_client.py` |
