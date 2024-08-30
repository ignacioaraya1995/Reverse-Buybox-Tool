### Quick Start Guide

#### What This Tool Does

sk = A3-3CF6Y7-XTRZXH-D8YB3-PPRP6-2M28M-6YQFA

This tool helps you analyze real estate data by letting you choose between two types of analyses: Market Reverse Buybox (MRBB) and Reverse Buybox (RBB). You can pick a specific client's data and decide if you want to analyze just MRBB, or both MRBB and RBB. The tool then processes the data, giving you detailed reports and insights.

#### Getting Started

##### Setting Up

1. **Install Python**: Make sure you have Python 3.x installed.
2. **Install Dependencies**: Run `pip install pandas` to install pandas, and add any other necessary packages.
3. **Download the Tool**: Clone or download this tool to your computer.
   ```
   git clone [Repository URL]
   ```
4. **Organize Your Data**: Create an `input` folder in the tool's directory. Inside `input`, make a folder for each client with their raw data. If you're doing an RBB analysis, add a `client deals` folder in each client's folder with a file named like `Client Name - client_deals.xlsx`.

##### Directory Structure

- **`input/`**: Place client folders here. Each client folder can have county data files and a `client deals` subfolder for RBB analysis.
- **`outcome/`**: The tool saves its reports and processed data here.

Example structure:

```
/project_root/
│
├── input/
│   ├── Client Name 1/
│   │   ├── county_data.csv
│   │   └── client deals/
│   │       └── Client Name 1 - client_deals.xlsx
│   ...
│
└── outcome/
```

#### Using the Tool

1. **Run the Tool**: Open a command line, navigate to the tool's folder, and run `python [script_name].py`.
2. **Choose a Client**: The tool will show a list of clients. Type the number of the client you want to analyze.
3. **Pick the Analysis Type**: Type `MRBB` for only MRBB analysis or `Both` for MRBB and RBB.

#### Troubleshooting

- **If RBB Fails**: Check the Excel file name and ensure it has the correct format and columns.
- **Large Datasets**: If the tool uses too much memory, ensure your computer has enough RAM to handle the data.

---
