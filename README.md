# laplace_opt

PyQt6-based GUI application for **Laplace optimization** workflows.

This package provides a desktop application with a structured logging system and optional server protocol integration. It is designed to launch an interactive optimization window (`OptWindow`) and handle data and logs cleanly, suitable for research and scientific workflows.

---

## Features

- PyQt6 graphical user interface
- Structured logging via `laplace_log`
- Using `laplace_server` protocol
- Entry point via `main.py`
- Modular design separating GUI, logging, and server logic

---

## Installation

Install dependencies:

```bash
pip install PyQt6 qdarkstyle botorch laplace-server laplace-log
```

---

## Run the code

To run the code use:

```bash
python -m laplace_opt.main
```

---

## Project Structure

```
laplace_opt/
├── laplace_opt/
│   ├── main.py                 # Entry point launching the GUI
│   ├── config.ini              # Default configuration
│   ├── interface/              # GUI window implementation
│   ├── core/                   # Optimization process
│   ├── model_construction/     # Optimization ressources
│   ├── utils/                  # Helpers
├── tests/                      # Test scripts
├── LICENSE                     # GPL-3.0 License
└── README.md                   # Project README
```

---

## Licence

GPL-3.0

---

## Status

This project is actively used in the LAPLACE ecosystem for optimization experiments. It is designed for controlled research environments and scientific workflows.