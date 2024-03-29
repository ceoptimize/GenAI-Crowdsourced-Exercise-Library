# CrowdSourced Exercise Database

This project harnesses Generative AI and eventually crowdsourcing to assemble a detailed database on fitness. Initially focusing on data collection and structuring via NoSQL and Postgres, the vision extends to developing a web application that empowers users to contribute, refine, and interact with the data, fostering a community-driven fitness knowledge platform.

## Description

This project leverages Generative AI, predominantly ChatGPT, to amass a comprehensive database in NoSQL, encompassing a wide array of fitness-related information, including exercises, muscle groups, equipment, and other pertinent attributes. The collected data undergoes a transformation and structuring process before being transferred to a Postgres database, where it's further aggregated to enhance its organization and accessibility.

The future roadmap for this project includes the development of a web application that will not only present this data in a user-friendly manner but also incorporate interactive features such as upvoting, downvoting, and content editing. These features aim to foster a community-driven platform where fitness aficionados can contribute, refine, and validate the content, ensuring its accuracy and relevance. This crowdsourced approach is designed to create a dynamic and evolving repository of fitness knowledge that benefits from collective expertise and insights.


## Usage

Once you have installed and set up the Crowdsourced Exercise Database, you can start utilizing its features to populate and interact with your fitness-related databases.

### Populating the Database

To populate the NoSQL and Postgres databases with fitness-related data:

1. Ensure your MongoDB and PostgreSQL services are running.
2. Execute the main script to start the data collection and structuring process:

```bash
python main.py
```
Note: The Postgres piece is still under development.

## Interacting with the Data
At this stage, the system primarily operates in the background to gather and structure the data. Interaction is designed for future web application development.
Developers can query the MongoDB or PostgreSQL databases to review the structured data, perform analyses, or export the data for other uses.

### Prerequisites/Dependencies

Ensure you have the following installed and configured for your development environment:

- **PostgreSQL**: Used for structured data storage. [Install PostgreSQL](https://www.postgresql.org/download/) and create a database for the project.

- **MongoDB**: Used for NoSQL data storage. [Install MongoDB](https://www.mongodb.com/try/download/community) and ensure it's running on your machine.

- **OpenAI API (ChatGPT)**: This project utilizes ChatGPT for generating and processing data. Obtain an API key by creating an account at [OpenAI](https://beta.openai.com/signup/).

- **YouTube API**: Necessary for fetching data related to videos. Get your API key by following the instructions on the [Google Cloud Console](https://console.cloud.google.com/).


### Installing

Clone the repository and set up the environment

```bash
git clone https://github.com/ceoptimize/GenAI-Crowdsourced-Exercise-Library.git
cd GenAI-Crowdsourced-Exercise-Library

```