#### Overview

This tool automates the processing of real estate data for both Market Reverse Buybox (MRBB) and Reverse Buybox (RBB) analyses. It allows users to select a client (based on client folders), choose the type of analysis to perform, and processes the data accordingly to generate reports and insights.

#### How It Works

The tool follows a structured workflow to process client data:

1. **Client Selection**: Users select a client from a list of available client folders.
2. **Analysis Type Selection**: Users choose whether to perform MRBB only or both MRBB and RBB.
3. **Data Processing**: The tool then performs a series of steps including deleting old CSV files, consolidating new data, processing CSV files, loading property details, exporting cases, and creating summary tables.

#### Workflow Diagram

[Insert a conceptual diagram here]

The diagram should visually represent the workflow steps mentioned above, illustrating the decision points (e.g., choosing MRBB or RBB) and the main processes (deleting files, consolidating CSVs, etc.).

#### Setup Instructions

1. **Prerequisites**: Ensure Python 3.x is installed on your system.
2. **Dependencies**: Install required Python packages via pip:
   ```
   pip install pandas
   [List other dependencies]
   ```
3. **Clone Repository**: Clone this repository to your local machine.
   ```
   git clone [Repository URL]
   ```
4. **Prepare Data**: Ensure your client data is structured in folders within an `input` directory at the root of the project.

#### Usage Guide

1. **Launch the Tool**: Run the script from the command line:
   ```
   python [script_name].py
   ```
2. **Select a Client**: Follow the prompt to select a client by entering the corresponding number.
3. **Select Analysis Type**: Enter 'MRBB' to run Market Reverse Buybox only, or 'Both' to run both analyses.

#### Troubleshooting

- **RBB Errors**: If an error occurs during RBB processing, check for correct file naming and ensure all required columns are present in the data.
- **Memory Issues**: For large datasets, ensure your system has sufficient memory available, as the `low_memory=False` setting in pandas can increase memory usage.

#### Support

For support, please create an issue in the GitHub repository or contact [Support Contact Information].

---

### Creating the Diagram

For the workflow diagram, you can use tools like Lucidchart, Draw.io, or even PowerPoint to create a visual representation of the process. The diagram should include:

- Start (User starts the script)
- Decision (Select client)
- Decision (Choose MRBB only or both MRBB and RBB)
- Processes (Listed as sequential steps: Delete CSVs, Consolidate CSVs, Process CSV File, Load Properties, Export Cases, Create Tables)
- End (Process completion)
