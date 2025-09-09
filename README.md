# Telegram Snowball Sampling Tool
![Main Image](https://github.com/thomasjjj/Telegram-Snowball-Sampling/assets/118008765/58cae690-b8cc-4b93-b073-809d888fe49e)

## Overview
The Telegram Snowball Sampling Tool is a Python-based utility designed for conducting comprehensive network analysis of Telegram channels through three main methods:

1. **Forwarded Messages** - Automatically discovers channels through message forwards
2. **Channel Recommendations** - Collects Telegram's built-in channel recommendations 
3. **URL Extraction** - Maps external connections by extracting URLs from messages

The tool creates detailed edge lists for network visualization and provides extensive analysis capabilities.

## Summary of Network Analysis in Telegram
This tool implements multiple discovery methods to map the complex network structure of Telegram channels:

### Snowball Sampling Through Message Forwards
Snowball sampling discovers channels through forwarded messages, starting with a seed channel and expanding outward. This method identifies both the origin and dissemination paths of information, creating a directed network structure.

### Channel Recommendations
The tool leverages Telegram's built-in recommendation algorithm to discover topically related channels. This provides additional network insights beyond just forward relationships.

### URL Extraction
By capturing external URLs shared in messages, the tool maps connections between Telegram channels and external websites, providing a more comprehensive view of the information ecosystem.

## Important Warning: Runtime Expectations

### Exponential Growth in Runtime
The Telegram Snowball Sampling Tool can take several days to complete its run due to the exponential nature of the sampling process. Each iteration potentially adds a new set of channels, growing exponentially (e.g., 3 channels in the first iteration can lead to 9 in the second and 27 in the third).

### Recommendations for Efficient Use
- **Limit Iterations**: Keep to 3 iterations or fewer to balance depth and runtime
- **Filter Forwards**: Focus on channels with multiple mentions to target relevant content
- **Limit Posts Per Channel**: Set a reasonable maximum for posts to check per channel
- **Adjust Feature Settings**: Selectively enable/disable recommendations and URL extraction based on your needs

## Features
- Automated discovery of Telegram channels through three methods:
  - Forwarded message tracking
  - Channel recommendations retrieval
  - URL extraction from messages
- Customizable parameters for depth, frequency thresholds, and scope
- Comprehensive edge list creation for network analysis 
- Network visualization ready output for tools like Gephi
- Network metrics calculation and analysis
- Environment-based configuration system
- Detailed logging for monitoring progress

## Project Structure
```
telegram-snowball-sampling/
├── config.py                 # Configuration manager
├── EdgeList.py               # Handles edge list creation
├── example_config.env        # Template environment variables
├── .env                      # Your environment variables (created from example_config.env)
├── main.py                   # Main application script
├── merge_csv_data.py         # CSV merging utility
├── network_analysis.py       # Network analysis script
├── recommendations.py        # Channel recommendations module
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── utils.py                  # Utility functions
├── EdgeList/                 # Created during execution - edge list files
├── merged/                   # Created during execution - merged results
├── network_analysis/         # Created during analysis - network metrics
└── results/                  # Created during execution - individual run results
```

## Requirements
- Python 3.6 or higher
- Telethon library
- A registered Telegram application (for API credentials)
- All dependencies listed in requirements.txt

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/telegram-snowball-sampling.git
cd telegram-snowball-sampling
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The tool automatically creates a `.env` file from the template and will prompt you for your Telegram API credentials when first run. You can also manually configure the following options in the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| TELEGRAM_API_ID | Your Telegram API ID | (required) |
| TELEGRAM_API_HASH | Your Telegram API Hash | (required) |
| TELEGRAM_SESSION_NAME | Name for the Telegram session | session_name |
| DEFAULT_MIN_MENTIONS | Minimum mentions threshold | 5 |
| DEFAULT_ITERATIONS | Number of iterations | 3 |
| DEFAULT_MAX_POSTS | Maximum posts to check per channel | 100 |
| DEFAULT_INCLUDE_RECOMMENDATIONS | Whether to include channel recommendations | True |
| DEFAULT_RECOMMENDATIONS_DEPTH | Maximum depth for recommendations | 2 |
| DEFAULT_INCLUDE_URLS | Whether to extract URLs from messages | True |
| RESULTS_FOLDER | Directory for storing results | results |
| MERGED_FOLDER | Directory for merged results | merged |
| EDGE_LIST_FOLDER | Directory for edge list files | EdgeList |
| EDGE_LIST_FILENAME | Name of the edge list file | Edge_List.csv |
| MERGED_FILENAME | Name of the merged file | merged_channels.csv |
| DEBUG | Enable debug logging | False |

## Usage

Run the main script:
```bash
python main.py
```

The script will:
1. Prompt for Telegram API credentials if not configured
2. Ask for seed channels (comma-separated)
3. Request parameters for iterations, minimum mentions, etc.
4. Begin the data collection process using all enabled methods
5. Save results to CSV and edge list files
6. Offer to run network analysis on the collected data

## Data Collection Methods

### 1. Forward Detection
Analyzes messages in each channel to find forwards from other channels. This reveals information flow between channels.

### 2. Channel Recommendations
Retrieves Telegram's own channel recommendations for each discovered channel. These recommendations are based on Telegram's algorithm which considers content similarity and user overlap.

### 3. URL Extraction
Extracts all URLs shared in messages across channels, creating connections between Telegram channels and external websites.

## Output Files

The tool generates several outputs:

1. **Individual Run Results** (in the `results` folder):
   - CSV files containing channel IDs, names, and usernames
   - URL lists from message content

2. **Edge List** (in the `EdgeList` folder):
   - CSV file with network connections, including:
     - Forward relationships
     - Recommendation relationships
     - URL connections
   - Connection types and weights for advanced analysis

3. **Merged Results** (in the `merged` folder):
   - Consolidated CSV with all unique channels found across multiple runs

4. **Network Analysis** (in the `network_analysis` folder, when analysis is run):
   - Network metrics in Excel format
   - Gephi-compatible GEXF file for visualization
   - Basic network visualization image

## Network Analysis

The included network analysis script (`network_analysis.py`) provides:

1. **Basic Network Metrics**:
   - Node and edge counts
   - Network density
   - Connected components
   - Average path length

2. **Key Influencer Identification**:
   - Top source channels (with most outgoing connections)
   - Top receiver channels (with most incoming connections)

3. **Connection Type Analysis**:
   - Distribution of connection types (forwards vs. recommendations vs. URLs)
   - Weight distribution analysis

4. **Visualization**:
   - Gephi-compatible GEXF file
   - Basic visualization image
   - Network metrics in Excel format

Run network analysis separately:
```bash
python network_analysis.py --edge-list EdgeList/Edge_List.csv --output-dir network_analysis
```

## Network Visualization with Gephi

For advanced network visualization:

1. Download and install [Gephi](https://gephi.org/)
2. Import the GEXF file from the network_analysis folder
3. Apply layouts like ForceAtlas2 to organize the network
4. Style nodes based on metrics like degree or betweenness
5. Run community detection algorithms to identify clusters

A detailed guide is created in the results folder after each run.

## Disclaimer
This tool is for educational and research purposes only. Please ensure that you comply with Telegram's terms of service and respect privacy and ethical guidelines when using this tool.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## Future Development
- Add language detection for message content filtering
- Implement community detection algorithms
- Add multi-API parallel processing for improved performance
- Create live network visualization capabilities
