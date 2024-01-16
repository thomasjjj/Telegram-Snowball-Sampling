# Telegram Snowball Sampling Tool
![Main Image](https://github.com/thomasjjj/Telegram-Snowball-Sampling/assets/118008765/58cae690-b8cc-4b93-b073-809d888fe49e)

## Overview
The Telegram Snowball Sampling Tool is a Python-based utility designed for conducting snowball sampling to collect Telegram channels through forwards. This script uses the Telethon library to interact with Telegram's API, allowing for the automated discovery and processing of Telegram channels based on message forwards.

## Summary of Snowball Sampling in Telegram Network Analysis
Snowball sampling is a strategic methodology employed in network analysis, particularly effective for investigating populations that are otherwise difficult to observe directly. This method is especially useful in the context of Telegram, a social network where channels and chats serve as nodes. These nodes are interconnected through forwards, mentions, and internal hyperlinks, which function as the network edges.

### Concept and Application in Telegram
In Telegram's complex network, the structure is not readily observable externally – channels generally need to be found to search the messages within them. Snowball sampling is thus an invaluable technique for mapping this concealed network. It begins with a selected initial sample (or 'seed') and expands through multiple steps, identifying relevant actors within this network through message forwards. The seed channel is crucial as it sets the direction and scope of the sampling. However, the choice of the seed can introduce biases, influencing the resulting sample and network representation.

### Data Collection and Expansion
Data in this method are typically gathered using Telegram's "export chat history" function, however, this process connects through the Telegram API to allow the user to directly connect to Telegram and automate the process. This approach is known as exponential discriminative snowball sampling. It starts with a seed channel, often one with connections to specific interest groups or populations. The process involves collecting forwards from this channel, which reveals both the origin and dissemination paths of the information. This dual nature of forwards - identifying both the forwarder and the forwarded - creates a directed network structure.

### Methodological Considerations
While effective, this technique can introduce certain distortions due to the non-random nature of the seed selection. This aspect necessitates careful consideration, especially when discussing methodological limitations.

### Implementation Strategies
Various strategies are employed to determine the expansion of the sample. For instance, one approach involves selecting a set number of prominent channels based on metrics like forwards, mentions, or links. Another strategy counts the distinct channels referencing a particular channel, mitigating the undue influence of larger channels. A combined approach evaluates channels based on the number of distinct references, balancing between prominence and diversity. This method can lead to the collection of a significant number of channels and messages, offering a comprehensive view of the network under study.

## Important Warning: Runtime Expectations

### Exponential Growth in Runtime
The Telegram Snowball Sampling Tool, while powerful, can potentially take several days (or drastically longer with more iterations) to complete its run. This extended runtime is due to the exponential nature of the snowball sampling process.

- **Exponential Process Explained**: In snowball sampling, each iteration potentially adds a new set of channels to be processed in the next iteration. For example, if each channel forwards messages from just three new channels, in the first iteration, you will process three channels, nine in the second iteration, and twenty-seven in the third iteration. This growth in the number of channels is exponential, meaning that each additional iteration can significantly increase the total number of channels to be processed, leading to a massive increase in runtime.

- **Impact of Additional Iterations**: Given this exponential growth, each additional iteration beyond the initial few can drastically increase the total runtime. Therefore, while the tool supports configuring the number of iterations, users should be mindful of this exponential increase in processing time.

### Recommendations for Efficient Use
- **Limit Iterations**: It's recommended to limit the process to three iterations for a balance between depth of search and practical runtime.
- **Filter Forwards**: To improve efficiency, consider filtering forwards to focus on channels that are commonly mentioned. This approach helps in targeting more relevant channels and reduces unnecessary processing.
- **Limit Posts Per Channel**: Another way to control runtime is by limiting the number of posts searched in each channel. This can significantly reduce the time taken per channel, especially for channels with a large number of posts.


## Features
- Automated collection of Telegram channels through snowball sampling.
- Customizable iteration depth, mention thresholds, and message processing limits.
- CSV output for easy analysis of collected data.

## Requirements
- Python 3.6 or higher.
- Telethon library.
- A registered Telegram application (for API credentials).

## Configuration
Edit the following parameters in the script as needed:
- `iterations`: Number of iterations for the snowball sampling.
- `min_mentions`: Minimum number of mentions for a channel to be included.
- `max_posts`: Maximum number of posts to check per channel (leave blank for no limit).

## Output Format
The output CSV file contains columns for each iteration, with each row representing a discovered channel. The format is as follows:
- `Iteration 1_id, Iteration 1_channelname, Iteration 2_id, Iteration 2_channelname, ...`

## Merging CSV Files

This section of the script is designed to efficiently merge data from multiple CSV files located in the `results` folder and compile them into a single CSV file. This process helps in consolidating data from various runs into a unified dataset.

### Functionality

- **Directory Check and Creation**: The script first checks for the existence of a `merged` directory. If this directory doesn't exist, it is automatically created.
- **Data Aggregation**: All CSV files within the `results` directory are processed. The script reads each file and extracts channel IDs and names, assuming these are located in alternating columns.
- **Duplicate Removal and Data Merging**: The new data is appended to any existing data in the `merged_channels.csv` file within the `merged` folder. The script ensures that only unique entries are retained, effectively removing any duplicates.
- **Appending New Data**: If `merged_channels.csv` already exists, the script appends new, unique data to it. If the file doesn't exist, it's created and populated with the merged data.

### Usage

Simply execute the script, and it will automatically process and merge the CSV files. The resulting file, `merged_channels.csv`, will be located in the `merged` directory.

```python
if __name__ == '__main__':
    # Specify the folders and filename
    results_folder = 'results'
    merged_folder = 'merged'
    merged_filename = 'merged_channels.csv'
    
    # Call the function to merge CSV files
    merge_csv_files(results_folder, merged_folder, merged_filename)
```

This script provides a seamless way to combine data from multiple iterations or runs, making data analysis and management more streamlined.


## Disclaimer
This tool is for educational and research purposes only. Please ensure that you comply with Telegram's terms of service and respect privacy and ethical guidelines when using this tool.

# TODO
**List of manageable and fun TODOs:**
- [x] Add per-find CSV/TXT file saves to prevent loss of data if execution is stopped early.
  - May want to make this optional depending on speed - but TG API rate limiting is the biggest bottleneck so impact expected to be minimal/negligible.
  - Consider alternative output formats.
- [ ] Output to Gephi and other network analysis formats.
- [x] Edgelist creation
- [ ] Add more detailed counts into the terminal feedback.
- [ ] Add possible estimation of time remaining based on statistical evaluation of progress (likely monte-carlo required).
- [ ] Analysis of forward messages to assign a source language (useful for additional filtering).
  - Lots of research papers covering this technique appear to add language filtering into the process. 
  - Building this in on a per-channel and per-forward message level would automate this process
- [ ] Statistical report of the process and findings (this may be useful for researchers identifying data biases).
  - List of all channels searched.
  - List of all forwards found (including those filtered out).
  - Some form of search ranking within the pool of analysed channels.
- [ ] Add option to scrape channel details and metadata on collection or at output to create a more detailed list overview. 
- [x] Added script to merge CSV results from multiple runs into a merged CSV with single list rather than lists per iteration.

**Harder TODOs – All contributions and suggestions are welcome:** 
- [ ] Add multi-API parallel processing to speed the process (will need more advanced queue assignment).
- [ ] Live visualisation of growing network.